%% ===========================================================================
% train_references.m - 语音数字识别参考库训练脚本
% ===========================================================================
% 功能：从音频文件批量提取特征，构建识别参考库
%
% 用法：
%   1. 将数字 0~10 的音频文件放入指定文件夹
%      文件命名示例：num0.wav, num1.mp3, 2.wav, digit_3.m4a, sample_10.wav
%   2. 在下方设置文件夹路径和参数
%   3. 运行脚本 >> train_references
%
% 注意：
%   - 文件名需包含对应数字 (0~10)
%   - 每个数字可录制多个样本以提高鲁棒性
%   - 支持 .wav, .mp3, .m4a, .ogg, .flac 格式
% ===========================================================================

clear; clc;

%% ==================== 参数设置 ====================
% 音频文件夹路径（修改为你的训练数据路径）
train_folder = fullfile(pwd, 'training_data');

% 如果没有训练数据文件夹，提示用户
if ~exist(train_folder, 'dir')
    fprintf('训练数据文件夹不存在: %s\n', train_folder);
    fprintf('请创建该文件夹并将 0~10 的音频文件放入其中。\n');
    fprintf('\n支持的命名方式：num0.wav, 1.mp3, digit_2.m4a, sample_10.wav 等\n');

    choice = input('\n是否创建该文件夹？(y/n): ', 's');
    if lower(choice) == 'y'
        mkdir(train_folder);
        fprintf('文件夹已创建: %s\n', train_folder);
        fprintf('请将音频文件放入该文件夹后重新运行此脚本。\n');
    end
    return;
end

% 特征提取参数
fs      = 44100;   % 统一采样率
f_max   = 4000;    % 分析频率上限 (Hz)
n_bins  = 256;     % 标准化频率点数
frac    = 0.3;     % 加窗比例（能量最大的30%）
adc_bit = 16;      % ADC 位数

%% ==================== 扫描音频文件 ====================
fprintf('==========================================================\n');
fprintf('  语音数字识别 — 参考库训练\n');
fprintf('==========================================================\n\n');
fprintf('训练文件夹: %s\n', train_folder);
fprintf('扫描音频文件中...\n');

file_list = dir(fullfile(train_folder, '*.*'));
audio_files = {};
for i = 1:length(file_list)
    [~, ~, ext] = fileparts(file_list(i).name);
    if any(strcmpi(ext, {'.wav', '.mp3', '.m4a', '.ogg', '.flac', '.wma'}))
        audio_files{end+1} = file_list(i).name; %#ok<AGROW>
    end
end

fprintf('找到 %d 个音频文件。\n', length(audio_files));
if isempty(audio_files)
    fprintf('没有找到音频文件，请将文件放入训练文件夹。\n');
    return;
end

%% ==================== 初始化参考库 ====================
ref_features = struct();
for d = 0:10
    ref_features(d+1).digit = d;
    ref_features(d+1).features = [];
end

%% ==================== 处理每个音频文件 ====================
fprintf('\n开始处理音频文件...\n');
fprintf('%-4s %-30s %-8s %-s\n', '序号', '文件名', '数字', '状态');

loaded_count = 0;
error_count = 0;

for f_idx = 1:length(audio_files)
    filename = audio_files{f_idx};
    [~, name, ~] = fileparts(filename);

    % 提取数字
    digit_val = extractDigitFromName(name);
    if isnan(digit_val) || digit_val < 0 || digit_val > 10
        fprintf('%-4d %-30s %-8s %s\n', f_idx, filename, '?', '✗ 无法识别数字');
        error_count = error_count + 1;
        continue;
    end

    % 读取音频
    try
        full_path = fullfile(train_folder, filename);
        [y, fs_file] = audioread(full_path);

        % 转单声道
        if size(y, 2) > 1
            y = mean(y, 2);
        end

        % 重采样
        if fs_file ~= fs
            y = resample(y, fs, fs_file);
        end

        % 预处理
        [proc_y, ~] = preprocessAudio(y, fs, frac);

        if length(proc_y) < 500
            fprintf('%-4d %-30s %-8s %s\n', f_idx, filename, ...
                num2str(digit_val), '✗ 有效音频太短');
            error_count = error_count + 1;
            continue;
        end

        % 提取特征
        feat = extractFeatures(proc_y, fs, f_max, n_bins);

        % 存储
        ref_features(digit_val + 1).features = ...
            [ref_features(digit_val + 1).features; feat];

        fprintf('%-4d %-30s %-8s %s\n', f_idx, filename, ...
            num2str(digit_val), '✓ 成功');
        loaded_count = loaded_count + 1;

    catch ME
        fprintf('%-4d %-30s %-8s %s\n', f_idx, filename, ...
            num2str(digit_val), ['✗ 错误: ' ME.message]);
        error_count = error_count + 1;
    end
end

%% ==================== 统计报告 ====================
fprintf('\n--- 处理统计 ---\n');
fprintf('成功: %d 个样本\n', loaded_count);
fprintf('失败: %d 个样本\n', error_count);
fprintf('\n各数字样本数:\n');
fprintf('  数字  |');
for d = 0:10
    fprintf(' %3d', d);
end
fprintf('\n  样本数|');
has_data = false(1, 11);
for d = 0:10
    n = size(ref_features(d+1).features, 1);
    fprintf(' %3d', n);
    if n > 0
        has_data(d+1) = true;
    end
end
fprintf('\n');

missing_digits = find(~has_data) - 1;
if ~isempty(missing_digits)
    fprintf('\n⚠ 警告：以下数字缺少训练样本: ');
    fprintf('%d ', missing_digits);
    fprintf('\n请补充对应的音频文件以提高识别率。\n');
end

%% ==================== 保存参考库 ====================
weights = struct(...
    'mag_corr',      0.55, ...
    'centroid',      0.22, ...
    'rolloff',       0.13, ...
    'group_delay',   0.10  ...
);
config = struct('fs', fs, 'f_max', f_max, 'version', 2);

% 保存到项目 data 目录
data_dir = fullfile(fileparts(mfilename('fullpath')), 'data');
if ~exist(data_dir, 'dir')
    mkdir(data_dir);
end

save(fullfile(data_dir, 'ref_features.mat'), 'ref_features', 'weights', 'config');

fprintf('\n✓ 参考特征库已保存到: %s\n', fullfile(data_dir, 'ref_features.mat'));
fprintf('  可直接运行 DigitRecognitionGUI 进行识别。\n');
fprintf('==========================================================\n');

%% ==================== 工具函数 ====================

function [sub_audio, start_idx] = preprocessAudio(audio, fs, frac)
    N = length(audio);
    frame_len = round(0.02 * fs);
    frame_shift = round(0.01 * fs);
    n_frames = floor((N - frame_len) / frame_shift) + 1;

    if n_frames < 3
        sub_audio = audio; start_idx = 1;
    else
        energy = zeros(n_frames, 1);
        for i = 1:n_frames
            idx = (i-1)*frame_shift + 1;
            energy(i) = sum(audio(idx:idx+frame_len-1).^2);
        end
        sorted_e = sort(energy);
        noise_floor = mean(sorted_e(1:max(1, round(0.2 * n_frames))));
        thresh = max(noise_floor * 3, 0.01 * max(energy));
        speech_mask = energy > thresh;
        first_frame = find(speech_mask, 1, 'first');
        last_frame  = find(speech_mask, 1, 'last');
        if isempty(first_frame)
            [~, start_idx] = maxSumSubArray(abs(audio), frac);
            window_len = floor(frac * N);
            end_idx = min(start_idx + window_len - 1, N);
            start_idx = max(start_idx, 1);
        else
            start_idx = max(1, (first_frame-1)*frame_shift + 1 - round(0.05*fs));
            end_idx   = min(N, last_frame*frame_shift + frame_len + round(0.05*fs));
        end
        sub_audio = audio(start_idx:end_idx);
    end
    win = hamming(length(sub_audio));
    sub_audio = sub_audio .* win;
end

function features = extractFeatures(audio, fs, f_max, ~)
    % 固定 FFT + 对数频带合并
    N = length(audio);
    N_fft_fixed = 2^14;
    X = fft(audio, N_fft_fixed);
    X_half = X(1:floor(N_fft_fixed/2)+1);
    f = (0:length(X_half)-1)' * fs / N_fft_fixed;

    mask = f <= f_max;
    f_voice = f(mask);
    X_voice = X_half(mask);

    mag = abs(X_voice);
    if max(mag) < eps, mag = ones(size(mag)); end
    mag_norm = mag / max(mag);

    % 倒谱提升去除音调影响
    mag_log = log(mag_norm + 1e-6);
    mag_log_sym = [mag_log; flipud(mag_log(2:end-1))];
    cepstrum = real(ifft(mag_log_sym));
    n_lifter = 35;
    cep_lift = zeros(size(cepstrum));
    cep_lift(1:n_lifter) = cepstrum(1:n_lifter);
    cep_lift(end-n_lifter+2:end) = cepstrum(end-n_lifter+2:end);
    mag_env_log = real(fft(cep_lift));
    mag_env_log = mag_env_log(1:length(mag_log));
    mag_env = exp(mag_env_log);
    mag_env = mag_env / max(mag_env);

    phase_raw = angle(X_voice);
    phase_unwrap = unwrap(phase_raw);

    if length(phase_unwrap) >= 3
        df_bin = f_voice(2) - f_voice(1);
        group_delay = -gradient(phase_unwrap) / (2 * pi * df_bin);
        try
            group_delay = medfilt1(group_delay, 3);
        catch
            group_delay = movmean(group_delay, 3);
        end
    else
        group_delay = zeros(size(phase_unwrap));
    end

    centroid = sum(f_voice .* mag) / (sum(mag) + eps);
    cum_energy = cumsum(mag.^2);
    rolloff_idx = find(cum_energy >= 0.85 * cum_energy(end), 1);
    if isempty(rolloff_idx), rolloff_idx = length(cum_energy); end
    rolloff = f_voice(rolloff_idx);

    % 频带合并（降维去噪）
    n_bands_target = 180;
    band_edges = round(logspace(log10(50), log10(f_max), n_bands_target + 1));
    band_edges = unique(band_edges);
    n_bands = length(band_edges) - 1;
    mag_band = zeros(n_bands, 1); phase_band = zeros(n_bands, 1);
    gd_band = zeros(n_bands, 1); f_band = zeros(n_bands, 1);
    for b = 1:n_bands
        bin_mask = (f_voice >= band_edges(b)) & (f_voice < band_edges(b+1));
        if any(bin_mask)
            mag_band(b) = mean(mag_env(bin_mask));  % 用包络而非原始谱
            phase_band(b) = mean(phase_unwrap(bin_mask));
            gd_band(b) = mean(group_delay(bin_mask));
            f_band(b) = mean(f_voice(bin_mask));
        end
    end

    features = struct();
    features.freq_axis      = f_voice;
    features.mag_norm       = mag_norm;
    features.phase_unwrap   = phase_unwrap;
    features.group_delay    = group_delay;
    features.freq_match     = f_band;
    features.mag_match      = mag_band;
    features.phase_match    = phase_band;
    features.gd_match       = gd_band;
    features.centroid       = centroid;
    features.rolloff        = rolloff;
    features.N_orig         = N;
    features.N_fft          = N_fft_fixed;
    features.n_bins         = length(f_voice);
    features.n_bands        = n_bands;
end

function [maxSubArray, startIndex, maxSum] = maxSumSubArray(arr, fraction)
    n = length(arr);
    windowSize = floor(n * fraction);
    windowSize = max(windowSize, 1);
    if windowSize > n, windowSize = n; end

    currentSum = sum(arr(1:windowSize));
    maxSum = currentSum;
    startIndex = 1;

    for i = 2:(n - windowSize + 1)
        currentSum = currentSum - arr(i - 1) + arr(i + windowSize - 1);
        if currentSum > maxSum
            maxSum = currentSum;
            startIndex = i;
        end
    end
    maxSubArray = arr(startIndex:(startIndex + windowSize - 1));
end

function digit = extractDigitFromName(filename)
    if contains(filename, '10') || contains(filename, 'ten')
        digit = 10;
        return;
    end
    tokens = regexp(filename, '(?<!\d)(\d)(?!\d)', 'tokens');
    for t_idx = 1:length(tokens)
        val = str2double(tokens{t_idx}{1});
        if val >= 0 && val <= 9
            digit = val;
            return;
        end
    end
    digit = NaN;
end
