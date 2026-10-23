% 实验3：补零对频谱的影响

clear; close all;

% 参数设置
fs = 1000;
f0 = 50;
N_data = 64;                    % 实际数据点数
t = (0:N_data-1)' / fs;
x = sin(2*pi * f0 * t);

% 加汉明窗，减少泄漏干扰
x = x .* hamming(N_data);

zero_pad_multiples = [1, 2, 4, 8, 16, 32];

% 绘图
figure('Position', [100, 100, 1400, 800]);

for i = 1:6
    N_fft = N_data * zero_pad_multiples(i);

    X = fft(x, N_fft);             % 自动补零到 N_fft 点
    X_mag = abs(X) / N_data;       % 用实际数据长度归一化
    X_mag(2:N_fft) = 2 * X_mag(2:N_fft);

    f_axis = (0:N_fft-1) * fs / N_fft;
    half_idx = floor(N_fft / 2);

    subplot(2, 3, i);

    stem(f_axis(1:half_idx), X_mag(1:half_idx), '.', ...
         'MarkerSize', 5, 'Color', 'b');
    hold on;

    % 标注 50Hz
    xline(f0, 'r--', 'LineWidth', 1);

    xlabel('频率 (Hz)'); ylabel('幅值');
    title(sprintf('补零×%d  N_{fft}=%d  Δf=%.2f Hz', ...
           zero_pad_multiples(i), N_fft, fs/N_fft));
    grid on;
    xlim([0, 150]);
    ylim([0, 1.2]);
end

sgtitle(sprintf(['实验3：补零对频谱的影响\n' ...
    '实际数据长度 N=%d (%.0f ms)，补零仅增加频域采样密度'], ...
    N_data, N_data/fs*1000), 'FontSize', 12);

saveas(gcf, 'figures/exp3_zeropad.png');

% 输出说明
fprintf('\n  补零效果总结:\n');
fprintf('  实际数据点数 N_data = %d\n', N_data);
fprintf('  %-12s %-12s %s\n', '补零倍数', 'FFT点数', '频率间隔Δf');
fprintf('  %s\n', repmat('-', 1, 40));
for i = 1:6
    N_fft = N_data * zero_pad_multiples(i);
    fprintf('  ×%-10d %-12d %.3f Hz\n', zero_pad_multiples(i), N_fft, fs/N_fft);
end
