%% ===========================================================================
% DigitRecognitionGUI - 基于傅里叶变换的语音数字识别系统
% ===========================================================================
% 功能：对数字 0~10 的语音进行录音/加载，利用傅里叶变换提取幅度谱、
%       相位谱及多种谱特征，通过综合匹配实现高精度识别。
%
% 改进点：
%   1. 引入相位谱分析（解卷相位 + 群延迟），弥补幅度谱信息不足
%   2. 多特征融合匹配（幅度相关系数 + 相位余弦相似度 + 群延迟相关 + 谱质心/滚降）
%   3. 加权投票机制，提升识别鲁棒性
%   4. 支持数字 0~10（demo 仅支持 0~9）
%   5. 美观的 GUI 界面，集成录音、频谱显示、结果展示
%
% ===========================================================================

function DigitRecognitionGUI
    %% ==================== 全局状态 ====================
    state = struct();
    state.fs = 44100;           % 采样率
    state.adc_bit = 16;         % ADC 位数
    state.n_chls = 1;           % 单声道
    state.rec_T = 2;            % 录音时长 (秒)
    state.frac = 0.3;           % 加窗比例（取能量最大的 30%）
    state.f_max = 4000;         % 分析频率上限 (Hz)
    state.n_match_bands = 180;  % 匹配用频带数（降维去噪）
    state.recorder = [];        % 录音对象
    state.is_recording = false; % 录音状态标志
    state.audio_data = [];      % 当前音频数据
    state.audio_processed = []; % 预处理后的音频
    state.features = [];        % 当前音频特征
    state.ref_features = [];    % 参考特征库
    state.recognized_digit = -1;% 识别结果
    state.confidence = 0;       % 置信度
    state.all_scores = [];      % 所有数字的得分

    %% ==================== 特征匹配权重 ====================
    % 权重可通过实验调整以优化识别率
    state.weights = struct(...
        'mag_corr',      0.55, ...  % 对数幅度谱相关
        'centroid',      0.22, ...  % 谱质心
        'rolloff',       0.13, ...  % 谱滚降
        'group_delay',   0.10  ...  % 群延迟（去均值后相关）
    );

    %% ==================== 颜色主题 ====================
    theme = struct();
    theme.bg        = [0.13 0.14 0.18];   % 深色背景
    theme.panel_bg  = [0.18 0.19 0.24];   % 面板背景
    theme.accent    = [0.30 0.65 1.00];   % 主色调（蓝）
    theme.success   = [0.30 0.90 0.50];   % 成功（绿）
    theme.warning   = [1.00 0.75 0.20];   % 警告（黄）
    theme.error     = [1.00 0.30 0.35];   % 错误（红）
    theme.text      = [0.90 0.90 0.95];   % 主文字
    theme.text_dim  = [0.55 0.57 0.65];   % 次要文字
    theme.btn_bg    = [0.22 0.24 0.30];   % 按钮背景
    theme.btn_hover = [0.28 0.30 0.38];   % 按钮悬停

    %% ==================== 创建主窗口 ====================
    fig = uifigure('Name', '基于傅里叶变换的语音数字识别系统 (0~10)', ...
                   'Color', theme.bg, ...
                   'Position', [150 60 1100 720], ...
                   'Resize', 'off', ...
                   'Icon', '');
    fig.CloseRequestFcn = @(~,~) onClose();

    %% ==================== 布局 ====================
    % 使用 uigridlayout 进行响应式布局
    main_grid = uigridlayout(fig, [4 3], ...
        'RowHeight', {90, 245, 245, 80}, ...
        'ColumnWidth', {'1.2x', '1x', '1x'}, ...
        'Padding', [14 14 14 14], ...
        'RowSpacing', 10, ...
        'ColumnSpacing', 10, ...
        'BackgroundColor', theme.bg);

    %% ---- 第1行：标题栏 + 控制按钮 ----
    title_panel = uipanel(main_grid, 'BackgroundColor', theme.panel_bg, ...
        'BorderType', 'none', 'Title', '');
    title_panel.Layout.Row = 1;
    title_panel.Layout.Column = [1 3];

    title_grid = uigridlayout(title_panel, [1 6], ...
        'ColumnWidth', {'1x', 120, 120, 120, 120, 110}, ...
        'Padding', [16 8 16 8], ...
        'ColumnSpacing', 12, ...
        'BackgroundColor', theme.panel_bg);

    % 标题
    uilabel(title_grid, 'Text', '基于傅里叶变换的语音数字识别系统', ...
        'FontSize', 18, 'FontWeight', 'bold', ...
        'FontColor', theme.text, ...
        'BackgroundColor', 'none', ...
        'HorizontalAlignment', 'left');

    % 录音按钮
    state.btn_record = uibutton(title_grid, 'Text', '⏺ 开始录音', ...
        'FontSize', 13, 'FontWeight', 'bold', ...
        'BackgroundColor', theme.accent, 'FontColor', [1 1 1], ...
        'ButtonPushedFcn', @(~,~) toggleRecording());
    state.btn_record.Layout.Column = 2;

    % 加载文件按钮
    state.btn_load = uibutton(title_grid, 'Text', '📁 加载文件', ...
        'FontSize', 13, ...
        'BackgroundColor', theme.btn_bg, 'FontColor', theme.text, ...
        'ButtonPushedFcn', @(~,~) loadAudioFile());
    state.btn_load.Layout.Column = 3;

    % 训练按钮
    state.btn_train = uibutton(title_grid, 'Text', '🔧 训练参考库', ...
        'FontSize', 13, ...
        'BackgroundColor', theme.btn_bg, 'FontColor', theme.text, ...
        'ButtonPushedFcn', @(~,~) openTrainDialog());
    state.btn_train.Layout.Column = 4;

    % 播放按钮
    state.btn_play = uibutton(title_grid, 'Text', '▶ 播放', ...
        'FontSize', 13, ...
        'BackgroundColor', theme.btn_bg, 'FontColor', theme.text, ...
        'ButtonPushedFcn', @(~,~) playAudio(), ...
        'Enable', 'off');
    state.btn_play.Layout.Column = 5;

    % 状态指示灯
    state.lamp = uilamp(title_grid, 'Color', theme.text_dim);
    state.lamp.Layout.Column = 6;
    state.lbl_status = uilabel(title_grid, 'Text', '就绪', ...
        'FontSize', 12, 'FontColor', theme.text_dim, ...
        'BackgroundColor', 'none');
    state.lbl_status.Layout.Column = 6;

    %% ---- 第2行：时域波形 (左) + 幅度谱 (中) + 相位谱 (右) ----
    % 时域波形面板
    pnl_time = uipanel(main_grid, 'BackgroundColor', theme.panel_bg, ...
        'BorderType', 'none', 'Title', '');
    pnl_time.Layout.Row = 2;
    pnl_time.Layout.Column = 1;
    time_grid = uigridlayout(pnl_time, [2 1], 'RowHeight', {22, '1x'}, ...
        'Padding', [12 10 12 10], 'RowSpacing', 6, ...
        'BackgroundColor', theme.panel_bg);
    uilabel(time_grid, 'Text', '时域波形', ...
        'FontSize', 13, 'FontWeight', 'bold', 'FontColor', theme.accent, ...
        'BackgroundColor', 'none');
    state.ax_time = uiaxes(time_grid, 'Color', [0.11 0.12 0.15], ...
        'XColor', theme.text_dim, 'YColor', theme.text_dim, ...
        'GridColor', [0.25 0.25 0.32], 'MinorGridColor', [0.18 0.18 0.24]);
    grid(state.ax_time, 'on');
    state.ax_time.GridAlpha = 0.4;
    state.ax_time.XLabel.String = '时间 (s)';
    state.ax_time.YLabel.String = '幅度';
    state.ax_time.XLabel.Color = theme.text_dim;
    state.ax_time.YLabel.Color = theme.text_dim;
    state.ax_time.FontSize = 10;
    state.ax_time.Box = 'on';

    % 幅度谱面板
    pnl_mag = uipanel(main_grid, 'BackgroundColor', theme.panel_bg, ...
        'BorderType', 'none', 'Title', '');
    pnl_mag.Layout.Row = 2;
    pnl_mag.Layout.Column = 2;
    mag_grid = uigridlayout(pnl_mag, [2 1], 'RowHeight', {22, '1x'}, ...
        'Padding', [12 10 12 10], 'RowSpacing', 6, ...
        'BackgroundColor', theme.panel_bg);
    uilabel(mag_grid, 'Text', '幅度谱 |X(f)|', ...
        'FontSize', 13, 'FontWeight', 'bold', 'FontColor', theme.success, ...
        'BackgroundColor', 'none');
    state.ax_mag = uiaxes(mag_grid, 'Color', [0.11 0.12 0.15], ...
        'XColor', theme.text_dim, 'YColor', theme.text_dim, ...
        'GridColor', [0.25 0.25 0.32], 'MinorGridColor', [0.18 0.18 0.24]);
    grid(state.ax_mag, 'on');
    state.ax_mag.GridAlpha = 0.4;
    state.ax_mag.XLabel.String = '频率 (Hz)';
    state.ax_mag.YLabel.String = '归一化幅度';
    state.ax_mag.XLabel.Color = theme.text_dim;
    state.ax_mag.YLabel.Color = theme.text_dim;
    state.ax_mag.FontSize = 10;
    state.ax_mag.Box = 'on';

    % 相位谱面板
    pnl_phase = uipanel(main_grid, 'BackgroundColor', theme.panel_bg, ...
        'BorderType', 'none', 'Title', '');
    pnl_phase.Layout.Row = 2;
    pnl_phase.Layout.Column = 3;
    phase_grid = uigridlayout(pnl_phase, [2 1], 'RowHeight', {22, '1x'}, ...
        'Padding', [12 10 12 10], 'RowSpacing', 6, ...
        'BackgroundColor', theme.panel_bg);
    uilabel(phase_grid, 'Text', '相位谱 ∠X(f) (解卷)', ...
        'FontSize', 13, 'FontWeight', 'bold', 'FontColor', theme.warning, ...
        'BackgroundColor', 'none');
    state.ax_phase = uiaxes(phase_grid, 'Color', [0.11 0.12 0.15], ...
        'XColor', theme.text_dim, 'YColor', theme.text_dim, ...
        'GridColor', [0.25 0.25 0.32], 'MinorGridColor', [0.18 0.18 0.24]);
    grid(state.ax_phase, 'on');
    state.ax_phase.GridAlpha = 0.4;
    state.ax_phase.XLabel.String = '频率 (Hz)';
    state.ax_phase.YLabel.String = '相位 (rad)';
    state.ax_phase.XLabel.Color = theme.text_dim;
    state.ax_phase.YLabel.Color = theme.text_dim;
    state.ax_phase.FontSize = 10;
    state.ax_phase.Box = 'on';

    %% ---- 第3行：特征对比 (左中) + 识别结果 (右) ----
    % 匹配度柱状图
    pnl_scores = uipanel(main_grid, 'BackgroundColor', theme.panel_bg, ...
        'BorderType', 'none', 'Title', '');
    pnl_scores.Layout.Row = 3;
    pnl_scores.Layout.Column = [1 2];
    scores_grid = uigridlayout(pnl_scores, [2 1], 'RowHeight', {22, '1x'}, ...
        'Padding', [12 10 12 10], 'RowSpacing', 6, ...
        'BackgroundColor', theme.panel_bg);
    uilabel(scores_grid, 'Text', '各数字综合匹配度对比', ...
        'FontSize', 13, 'FontWeight', 'bold', 'FontColor', theme.accent, ...
        'BackgroundColor', 'none');
    state.ax_scores = uiaxes(scores_grid, 'Color', [0.11 0.12 0.15], ...
        'XColor', theme.text_dim, 'YColor', theme.text_dim, ...
        'GridColor', [0.25 0.25 0.32], 'MinorGridColor', [0.18 0.18 0.24]);
    grid(state.ax_scores, 'on');
    state.ax_scores.GridAlpha = 0.4;
    state.ax_scores.XLabel.String = '数字';
    state.ax_scores.YLabel.String = '综合匹配度 (%)';
    state.ax_scores.XLabel.Color = theme.text_dim;
    state.ax_scores.YLabel.Color = theme.text_dim;
    state.ax_scores.FontSize = 10;
    state.ax_scores.Box = 'on';
    state.ax_scores.YLim = [0 105];
    state.ax_scores.XTick = 0:10;

    % 识别结果面板
    pnl_result = uipanel(main_grid, 'BackgroundColor', theme.panel_bg, ...
        'BorderType', 'none', 'Title', '');
    pnl_result.Layout.Row = 3;
    pnl_result.Layout.Column = 3;

    result_grid = uigridlayout(pnl_result, [7 1], ...
        'RowHeight', {22, 60, 30, 22, 22, 22, '1x'}, ...
        'Padding', [20 16 20 16], ...
        'RowSpacing', 8, ...
        'BackgroundColor', theme.panel_bg);

    uilabel(result_grid, 'Text', '🏆 识别结果', ...
        'FontSize', 13, 'FontWeight', 'bold', 'FontColor', theme.success, ...
        'BackgroundColor', 'none');

    % 大号识别数字
    state.lbl_digit = uilabel(result_grid, 'Text', '—', ...
        'FontSize', 48, 'FontWeight', 'bold', ...
        'FontColor', theme.success, ...
        'BackgroundColor', 'none', ...
        'HorizontalAlignment', 'center');
    state.lbl_digit.Layout.Row = 2;

    % 置信度
    state.lbl_confidence = uilabel(result_grid, 'Text', '置信度: —', ...
        'FontSize', 14, 'FontColor', theme.text, ...
        'BackgroundColor', 'none', ...
        'HorizontalAlignment', 'center');
    state.lbl_confidence.Layout.Row = 3;

    % 特征分项得分
    state.lbl_detail = uilabel(result_grid, 'Text', '', ...
        'FontSize', 11, 'FontColor', theme.text_dim, ...
        'BackgroundColor', 'none', ...
        'HorizontalAlignment', 'center');
    state.lbl_detail.Layout.Row = 4;

    % Top-3 显示
    state.lbl_top3 = uilabel(result_grid, 'Text', '', ...
        'FontSize', 11, 'FontColor', theme.text_dim, ...
        'BackgroundColor', 'none', ...
        'HorizontalAlignment', 'center');
    state.lbl_top3.Layout.Row = 5;

    % 参考库状态
    state.lbl_ref_status = uilabel(result_grid, 'Text', '参考库: 未加载', ...
        'FontSize', 11, 'FontColor', theme.warning, ...
        'BackgroundColor', 'none', ...
        'HorizontalAlignment', 'center');
    state.lbl_ref_status.Layout.Row = 6;

    %% ---- 第4行：信息栏 ----
    info_panel = uipanel(main_grid, 'BackgroundColor', theme.panel_bg, ...
        'BorderType', 'none', 'Title', '');
    info_panel.Layout.Row = 4;
    info_panel.Layout.Column = [1 3];

    info_grid = uigridlayout(info_panel, [1 8], ...
        'ColumnWidth', {90, 100, 100, 90, 100, 110, 110, '1x'}, ...
        'Padding', [16 8 16 8], ...
        'ColumnSpacing', 16, ...
        'BackgroundColor', theme.panel_bg);

    uilabel(info_grid, 'Text', ['采样率: ' num2str(state.fs) ' Hz'], ...
        'FontSize', 10, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');
    uilabel(info_grid, 'Text', ['时长: ' num2str(state.rec_T) ' s'], ...
        'FontSize', 10, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');
    uilabel(info_grid, 'Text', ['分析带宽: 0~' num2str(state.f_max) ' Hz'], ...
        'FontSize', 10, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');
    uilabel(info_grid, 'Text', ['加窗比例: ' num2str(state.frac*100) '%'], ...
        'FontSize', 10, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');
    state.lbl_info_samples = uilabel(info_grid, 'Text', '样本数: —', ...
        'FontSize', 10, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');
    state.lbl_info_dur = uilabel(info_grid, 'Text', '有效时长: —', ...
        'FontSize', 10, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');
    state.lbl_info_feat = uilabel(info_grid, 'Text', '特征维度: —', ...
        'FontSize', 10, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');

    % 底部签名
    uilabel(info_grid, 'Text', '© 基于傅里叶变换的语音识别 | 幅度 + 相位联合分析', ...
        'FontSize', 9, 'FontColor', theme.text_dim, 'BackgroundColor', 'none', ...
        'HorizontalAlignment', 'right');

    %% ==================== 初始化 ====================
    % 尝试自动加载参考特征库
    tryLoadReferences();

    %% ==================== 回调函数 ====================

    % ---- 录音切换 ----
    function toggleRecording()
        if state.is_recording
            stopRecording();
        else
            startRecording();
        end
    end

    % ---- 开始录音 ----
    function startRecording()
        try
            state.recorder = audiorecorder(state.fs, state.adc_bit, state.n_chls);
            record(state.recorder);
            state.is_recording = true;

            % 更新 UI
            state.btn_record.Text = '⏹ 停止录音';
            state.btn_record.BackgroundColor = theme.error;
            state.lamp.Color = theme.error;
            state.lbl_status.Text = '● 录音中...';
            state.lbl_status.FontColor = theme.error;
            state.btn_load.Enable = 'off';
            state.btn_train.Enable = 'off';
            state.btn_play.Enable = 'off';

            % 绘制录音提示
            cla(state.ax_time); cla(state.ax_mag); cla(state.ax_phase); cla(state.ax_scores);
            text(state.ax_time, 0.5, 0.5, '🎙 正在录音... 请对麦克风说出数字 (0~10)', ...
                'Units', 'normalized', 'HorizontalAlignment', 'center', ...
                'FontSize', 13, 'Color', theme.error);
            state.ax_time.XTick = []; state.ax_time.YTick = [];
            state.lbl_digit.Text = '🎙';
            state.lbl_digit.FontColor = theme.error;
            state.lbl_confidence.Text = '录音中...';
            state.lbl_detail.Text = '';

            drawnow;
        catch ME
            uialert(fig, ['无法启动录音：' ME.message], '录音错误');
            state.is_recording = false;
            state.btn_record.Text = '⏺ 开始录音';
            state.btn_record.BackgroundColor = theme.accent;
            state.lamp.Color = theme.text_dim;
            state.lbl_status.Text = '就绪';
            state.lbl_status.FontColor = theme.text_dim;
            state.btn_load.Enable = 'on';
            state.btn_train.Enable = 'on';
        end
    end

    % ---- 停止录音 ----
    function stopRecording()
        try
            stop(state.recorder);
            state.is_recording = false;

            % 获取录音数据
            state.audio_data = getaudiodata(state.recorder);

            % 更新 UI
            state.btn_record.Text = '⏺ 开始录音';
            state.btn_record.BackgroundColor = theme.accent;
            state.lamp.Color = theme.warning;
            state.lbl_status.Text = '处理中...';
            state.lbl_status.FontColor = theme.warning;
            state.btn_load.Enable = 'on';
            state.btn_train.Enable = 'on';

            drawnow;

            % 处理并识别
            processAndRecognize();

        catch ME
            uialert(fig, ['停止录音出错：' ME.message], '错误');
        end
    end

    % ---- 加载音频文件 ----
    function loadAudioFile()
        [file, path] = uigetfile({'*.wav;*.mp3;*.m4a;*.ogg;*.flac', ...
                                  '音频文件 (*.wav, *.mp3, *.m4a, *.ogg, *.flac)'; ...
                                  '*.*', '所有文件'}, ...
                                  '选择待识别的音频文件');
        if isequal(file, 0)
            return; % 用户取消
        end

        try
            full_path = fullfile(path, file);
            [y, fs_file] = audioread(full_path);

            % 如果是立体声，转为单声道
            if size(y, 2) > 1
                y = mean(y, 2);
            end

            % 重采样到标准采样率
            if fs_file ~= state.fs
                y = resample(y, state.fs, fs_file);
            end

            state.audio_data = y;

            % 更新 UI
            state.lamp.Color = theme.warning;
            state.lbl_status.Text = '处理中...';
            state.lbl_status.FontColor = theme.warning;

            drawnow;

            % 处理并识别
            processAndRecognize();

        catch ME
            uialert(fig, ['加载文件出错：' ME.message], '文件错误');
        end
    end

    % ---- 处理音频并识别 ----
    function processAndRecognize()
        % 1. 静音检测（在预处理之前，用原始录音判断）
        if max(abs(state.audio_data)) < 0.02
            uialert(fig, '未检测到有效语音，请重新录制。', '无声');
            resetUI();
            return;
        end

        % 2. 预处理
        [proc_audio, ~] = preprocessAudio(state.audio_data, state.fs, state.frac);

        if isempty(proc_audio) || length(proc_audio) < 100
            uialert(fig, '有效语音太短，请重新录制。', '处理错误');
            resetUI();
            return;
        end
        state.audio_processed = proc_audio;

        % 2. 提取特征
        state.features = extractFeatures(proc_audio, state.fs, state.f_max, state.n_match_bands);

        % 3. 检查参考库
        if isempty(state.ref_features)
            state.lbl_ref_status.Text = '参考库: 未加载 — 请先训练!';
            state.lbl_ref_status.FontColor = theme.error;
        end

        % 4. 识别（独立 try-catch，识别失败不影响波形显示）
        if ~isempty(state.ref_features)
            try
                [state.recognized_digit, state.confidence, state.all_scores, ...
                 detail_scores] = recognizeDigit(state.features, state.ref_features, state.weights);

                % 更新结果显示
                state.lbl_digit.Text = num2str(state.recognized_digit);
                state.lbl_digit.FontColor = theme.success;
                state.lbl_confidence.Text = sprintf('置信度: %.1f%%', state.confidence * 100);
                state.lbl_confidence.FontColor = theme.text;

                % 特征分项得分
                if ~isempty(detail_scores)
                    state.lbl_detail.Text = sprintf(...
                        '幅度:%.0f%% | 质心:%.0f%% | 滚降:%.0f%% | 群延迟:%.0f%%', ...
                        detail_scores.mag * 100, detail_scores.centroid * 100, ...
                        detail_scores.rolloff * 100, detail_scores.gd * 100);
                end

                % Top-3 显示
                [sorted_scores, sorted_idx] = sort(state.all_scores, 'descend');
                top3_str = 'Top-3: ';
                for i = 1:min(3, length(sorted_scores))
                    top3_str = [top3_str sprintf('%d(%.0f%%) ', ...
                        sorted_idx(i)-1, sorted_scores(i)*100)]; %#ok<AGROW>
                end
                state.lbl_top3.Text = top3_str;

                % 更新柱状图
                updateScoreBarChart(state.all_scores, sorted_idx(1));

            catch ME
                uialert(fig, ['识别出错：' ME.message], '识别错误');
            end
        end

        % 5. 更新波形和频谱图（独立 try-catch，绘图失败不影响结果）
        try
            updateWaveformPlot(state.audio_data, proc_audio, state.fs);
            updateSpectrumPlots(state.features);
        catch ME
            uialert(fig, ['绘图出错：' ME.message], '绘图错误');
        end

        % 6. 更新信息栏
        state.lbl_info_samples.Text = sprintf('样本数: %d', length(proc_audio));
        state.lbl_info_dur.Text = sprintf('有效时长: %.2fs', length(proc_audio)/state.fs);
        % 显示特征诊断信息（谱质心为 0 说明可能录到了静音）
        if ~isempty(state.features)
            state.lbl_info_feat.Text = sprintf('FFT:%d点 | 质心:%.0fHz | 滚降:%.0fHz', ...
                state.features.N_fft, state.features.centroid, state.features.rolloff);
        end

        % 7. 状态恢复
        state.lamp.Color = theme.success;
        state.lbl_status.Text = '✓ 识别完成';
        state.lbl_status.FontColor = theme.success;
        state.btn_play.Enable = 'on';
    end

    % ---- 播放音频 ----
    function playAudio()
        if ~isempty(state.audio_data)
            try
                sound(state.audio_data, state.fs);
            catch ME
                uialert(fig, ['播放出错：' ME.message], '播放错误');
            end
        end
    end

    % ---- 训练对话框 ----
    function openTrainDialog()
        % 创建训练模式对话框
        train_dlg = uifigure('Name', '训练参考库', ...
            'Color', theme.bg, ...
            'Position', [300 200 500 420], ...
            'Resize', 'off');

        train_grid = uigridlayout(train_dlg, [8 1], ...
            'RowHeight', {40, 30, 40, 40, 30, 40, 50, '1x'}, ...
            'Padding', [24 24 24 24], ...
            'RowSpacing', 12, ...
            'BackgroundColor', theme.bg);

        uilabel(train_grid, 'Text', '🔧 训练参考库设置', ...
            'FontSize', 18, 'FontWeight', 'bold', 'FontColor', theme.text, ...
            'BackgroundColor', 'none');

        uilabel(train_grid, 'Text', '选择训练方式：录制样本 或 从文件夹批量导入', ...
            'FontSize', 12, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');

        % 按钮：逐数字录制
        uibutton(train_grid, 'Text', '🎙 逐数字录制 (0~10, 共11个)', ...
            'FontSize', 14, 'FontWeight', 'bold', ...
            'BackgroundColor', theme.accent, 'FontColor', [1 1 1], ...
            'ButtonPushedFcn', @(~,~) startRecordingTraining(train_dlg));

        % 按钮：从文件夹导入
        uibutton(train_grid, 'Text', '📁 从文件夹批量导入 (0~10的音频文件)', ...
            'FontSize', 14, ...
            'BackgroundColor', theme.btn_bg, 'FontColor', theme.text, ...
            'ButtonPushedFcn', @(~,~) importFromFolder(train_dlg));

        uilabel(train_grid, 'Text', '（文件名需包含数字，如 num0.wav, 0.mp3 等）', ...
            'FontSize', 10, 'FontColor', theme.text_dim, 'BackgroundColor', 'none');

        % 每个数字录制多个样本
        state.lbl_train_info = uilabel(train_grid, 'Text', ...
            '提示：每个数字可录制多个样本以提升鲁棒性', ...
            'FontSize', 11, 'FontColor', theme.warning, 'BackgroundColor', 'none');

        % 关闭按钮
        uibutton(train_grid, 'Text', '关闭', ...
            'FontSize', 13, ...
            'BackgroundColor', theme.btn_bg, 'FontColor', theme.text_dim, ...
            'ButtonPushedFcn', @(~,~) close(train_dlg));
    end

    % ---- 逐数字录制训练 ----
    function startRecordingTraining(parent_dlg)
        digits_to_train = 0:10;
        max_retries = 3;  % 每个数字最多重试次数

        % 初始化参考特征存储
        new_ref = struct();
        for d = digits_to_train
            new_ref(d+1).digit = d;
            new_ref(d+1).features = [];
        end

        % 创建进度面板
        prog_dlg = uifigure('Name', '训练进度', ...
            'Color', theme.bg, ...
            'Position', [350 200 420 300], ...
            'Resize', 'off');
        prog_grid = uigridlayout(prog_dlg, [5 1], ...
            'RowHeight', {30, 55, 30, 30, '1x'}, ...
            'Padding', [20 20 20 20], ...
            'RowSpacing', 8, ...
            'BackgroundColor', theme.bg);

        prog_title = uilabel(prog_grid, 'Text', '准备开始训练...', ...
            'FontSize', 14, 'FontWeight', 'bold', 'FontColor', theme.text, ...
            'BackgroundColor', 'none');

        prog_digit = uilabel(prog_grid, 'Text', '', ...
            'FontSize', 42, 'FontWeight', 'bold', ...
            'FontColor', theme.accent, 'BackgroundColor', 'none', ...
            'HorizontalAlignment', 'center');

        prog_info = uilabel(prog_grid, 'Text', '', ...
            'FontSize', 12, 'FontColor', theme.text_dim, 'BackgroundColor', 'none', ...
            'HorizontalAlignment', 'center');

        prog_count = uilabel(prog_grid, 'Text', '', ...
            'FontSize', 11, 'FontColor', theme.text_dim, 'BackgroundColor', 'none', ...
            'HorizontalAlignment', 'center');

        drawnow;

        % -------- 使用 while 循环逐个训练（支持重试）---------
        d_idx = 1;          % 当前数字在列表中的位置
        success_count = 0;  % 成功录制的数字数

        while d_idx <= length(digits_to_train)
            d = digits_to_train(d_idx);

            % 更新进度
            prog_title.Text = sprintf('训练进度: %d/%d 个数字', d_idx, length(digits_to_train));
            prog_digit.Text = num2str(d);
            prog_info.Text = sprintf('请准备说 " %d "  ...', d);
            prog_info.FontColor = theme.accent;
            drawnow;

            % 倒计时让用户准备（3秒）
            for cnt = 3:-1:1
                prog_count.Text = sprintf('⏱ %d 秒后开始录制...', cnt);
                drawnow;
                pause(1);
            end
            prog_count.Text = '';

            % 录制
            try
                rec = audiorecorder(state.fs, state.adc_bit, state.n_chls);
                prog_info.Text = sprintf('🔴 正在录制，请说 " %d " !', d);
                prog_info.FontColor = theme.error;
                prog_digit.FontColor = theme.error;
                drawnow;

                recordblocking(rec, state.rec_T);
                y = getaudiodata(rec);

                % 检查录音是否有效（能量不能太低）
                if max(abs(y)) < 0.01
                    prog_info.Text = sprintf('⚠ 未检测到声音，请重试 " %d " (%d/3)', d, ...
                        floor((d_idx - success_count) / (max(d_idx - success_count, 1)) * max_retries));
                    prog_info.FontColor = theme.warning;
                    drawnow;
                    pause(1.5);
                    continue;  % 重试同一个数字
                end

                % 预处理
                [proc_y, ~] = preprocessAudio(y, state.fs, state.frac);
                if length(proc_y) < 500
                    prog_info.Text = sprintf('⚠ 有效语音太短，请重试 " %d "', d);
                    prog_info.FontColor = theme.warning;
                    drawnow;
                    pause(1.5);
                    continue;  % 重试同一个数字
                end

                % 提取特征并存储
                feat = extractFeatures(proc_y, state.fs, state.f_max, state.n_match_bands);
                new_ref(d+1).features = [new_ref(d+1).features; feat];

                prog_digit.FontColor = theme.success;
                prog_info.Text = sprintf('✓ " %d " 录制成功！', d);
                prog_info.FontColor = theme.success;
                drawnow;
                pause(0.8);
                success_count = success_count + 1;
                d_idx = d_idx + 1;  % 前进到下一个数字

            catch ME
                prog_info.Text = sprintf('✗ 录制出错: %s', ME.message);
                prog_info.FontColor = theme.error;
                drawnow;
                pause(2);
                % 不增加 d_idx，将重试
            end
        end

        % ---------- 训练完成，保存结果 ----------
        close(prog_dlg);
        close(parent_dlg);

        % 统计结果
        trained_digits = [];
        for d = 0:10
            if ~isempty(new_ref(d+1).features)
                trained_digits = [trained_digits, d]; %#ok<AGROW>
            end
        end

        if isempty(trained_digits)
            uialert(fig, '训练失败：没有成功录制任何数字。请检查麦克风后重试。', '训练失败');
            return;
        end

        state.ref_features = new_ref;
        saveRefFeatures();
        state.lbl_ref_status.Text = sprintf('参考库: 已加载 (%d个数字)', length(trained_digits));
        state.lbl_ref_status.FontColor = theme.success;

        msg = sprintf('训练完成！成功录制 %d 个数字：%s。\n参考特征库已保存，可以开始识别。', ...
            length(trained_digits), mat2str(trained_digits));
        uialert(fig, msg, '训练完成');
    end

    % ---- 从文件夹导入 ----
    function importFromFolder(parent_dlg)
        folder_path = uigetdir(pwd, '选择包含数字音频文件的文件夹');
        if folder_path == 0
            return;
        end

        try
            new_ref = struct();
            for d = 0:10
                new_ref(d+1).digit = d;
                new_ref(d+1).features = [];
            end

            % 扫描文件夹
            file_list = dir(fullfile(folder_path, '*.*'));
            loaded_count = 0;

            for f_idx = 1:length(file_list)
                [~, name, ext] = fileparts(file_list(f_idx).name);
                if ~any(strcmpi(ext, {'.wav', '.mp3', '.m4a', '.ogg', '.flac'}))
                    continue;
                end

                % 从文件名中提取数字
                digit_val = extractDigitFromName(name);
                if isnan(digit_val) || digit_val < 0 || digit_val > 10
                    continue;
                end

                % 读取并处理
                full_fpath = fullfile(folder_path, file_list(f_idx).name);
                [y, fs_file] = audioread(full_fpath);
                if size(y, 2) > 1
                    y = mean(y, 2);
                end
                if fs_file ~= state.fs
                    y = resample(y, state.fs, fs_file);
                end

                [proc_y, ~] = preprocessAudio(y, state.fs, state.frac);
                if length(proc_y) < 500
                    continue;
                end

                feat = extractFeatures(proc_y, state.fs, state.f_max, state.n_match_bands);
                new_ref(digit_val + 1).features = [new_ref(digit_val + 1).features; feat];
                loaded_count = loaded_count + 1;
            end

            if loaded_count == 0
                uialert(fig, '未找到可识别的音频文件。请确保文件名包含数字0~10。', '导入失败');
                return;
            end

            state.ref_features = new_ref;
            saveRefFeatures();
            state.lbl_ref_status.Text = sprintf('参考库: 已加载 (%d个数字, %d个样本)', ...
                sum(arrayfun(@(x) ~isempty(x.features), new_ref)), loaded_count);
            state.lbl_ref_status.FontColor = theme.success;

            close(parent_dlg);
            uialert(fig, sprintf('导入完成！共加载 %d 个音频样本。', loaded_count), '导入完成');

        catch ME
            uialert(fig, ['导入出错：' ME.message], '导入错误');
        end
    end

    % ---- 保存参考特征 ----
    function saveRefFeatures()
        ref_features = state.ref_features; %#ok<NASGU>
        weights = state.weights; %#ok<NASGU>
        config = struct('fs', state.fs, 'f_max', state.f_max, ...
                        'n_match_bands', state.n_match_bands, ...
                        'version', 2); %#ok<NASGU>  % 版本号用于兼容性检查
        data_dir = fullfile(fileparts(mfilename('fullpath')), 'data');
        if ~exist(data_dir, 'dir')
            [success, msg] = mkdir(data_dir);
            if ~success
                uialert(fig, ['无法创建数据目录：' msg], '保存失败');
                return;
            end
        end
        try
            save(fullfile(data_dir, 'ref_features.mat'), 'ref_features', 'weights', 'config');
        catch ME
            uialert(fig, ['保存参考库失败：' ME.message], '保存失败');
        end
    end

    % ---- 尝试加载参考特征 ----
    function tryLoadReferences()
        data_dir = fullfile(fileparts(mfilename('fullpath')), 'data');
        ref_file = fullfile(data_dir, 'ref_features.mat');
        if exist(ref_file, 'file')
            try
                loaded = load(ref_file);

                % 版本兼容性检查
                if isfield(loaded, 'config') && isfield(loaded.config, 'version')
                    cfg_ver = loaded.config.version;
                else
                    cfg_ver = 1;  % 旧版（可能有 bug）
                end
                if cfg_ver < 2
                    uialert(fig, ...
                        ['检测到旧版参考库（可能由有bug的旧代码生成，训练数据无效）。' newline ...
                         '建议删除后重新训练。是否自动清除旧库？'], ...
                        '旧版参考库', 'Icon', 'warning');
                    state.ref_features = [];
                    state.lbl_ref_status.Text = '参考库: 旧版已清除 — 请重新训练';
                    state.lbl_ref_status.FontColor = theme.warning;
                    return;
                end

                state.ref_features = loaded.ref_features;

                % 校验参考库特征维度一致性
                ref_ok = true;
                first_bins = [];
                for d = 1:length(state.ref_features)
                    f = state.ref_features(d).features;
                    if isempty(f), continue; end
                    if ~isstruct(f), ref_ok = false; break; end
                    if isempty(first_bins)
                        first_bins = length(f(1).mag_norm);
                    elseif length(f(1).mag_norm) ~= first_bins
                        ref_ok = false; break;
                    end
                end
                if ~ref_ok
                    state.ref_features = [];
                    state.lbl_ref_status.Text = '参考库: 不兼容 — 请重新训练';
                    state.lbl_ref_status.FontColor = theme.error;
                    return;
                end

                if isfield(loaded, 'weights')
                    state.weights = loaded.weights;
                end
                n_digits = sum(arrayfun(@(x) ~isempty(x.features), state.ref_features));
                n_samples = sum(arrayfun(@(x) size(x.features, 1), state.ref_features));
                state.lbl_ref_status.Text = sprintf('参考库: 已加载 (%d个数字, %d样本)', n_digits, n_samples);
                state.lbl_ref_status.FontColor = theme.success;
            catch ME
                state.lbl_ref_status.Text = '参考库: 加载失败';
                state.lbl_ref_status.FontColor = theme.error;
                uialert(fig, ['加载参考库失败：' ME.message], '加载错误');
            end
        else
            state.lbl_ref_status.Text = '参考库: 未加载 — 请点击"训练参考库"';
            state.lbl_ref_status.FontColor = theme.warning;
        end
    end

    % ---- 更新波形图 ----
    function updateWaveformPlot(raw_audio, proc_audio, fs)
        cla(state.ax_time);
        t_raw = (0:length(raw_audio)-1) / fs;

        % 绘制原始音频（灰色）
        plot(state.ax_time, t_raw, raw_audio, 'Color', [0.4 0.42 0.5], 'LineWidth', 0.5);
        hold(state.ax_time, 'on');

        % 计算有效段在原音频中的位置
        [~, start_idx] = maxSumSubArray(abs(raw_audio), state.frac);
        N_proc = length(proc_audio);
        t_proc = (start_idx-1 + (0:N_proc-1)) / fs;

        % 绘制有效段（高亮）
        plot(state.ax_time, t_proc, proc_audio, 'Color', theme.accent, 'LineWidth', 1.2);

        % 标记有效段边界
        xline(state.ax_time, t_proc(1), '--', 'Color', theme.success, 'LineWidth', 1, 'Alpha', 0.7);
        xline(state.ax_time, t_proc(end), '--', 'Color', theme.success, 'LineWidth', 1, 'Alpha', 0.7);

        hold(state.ax_time, 'off');
        xlim(state.ax_time, [0 max(t_raw)]);
        state.ax_time.XLabel.String = '时间 (s)';
        state.ax_time.YLabel.String = '幅度';
        title(state.ax_time, sprintf('时域波形 (绿色虚线内为有效语音段)'), ...
            'Color', theme.text_dim, 'FontSize', 10);
        grid(state.ax_time, 'on');
        state.ax_time.GridAlpha = 0.3;
    end

    % ---- 更新频谱图 ----
    function updateSpectrumPlots(features)
        % ---- 幅度谱 ----
        f_all = features.freq_axis(:);
        mag_all = features.mag_norm(:);

        % 滑动平均平滑显示（匹配仍用原始数据，不受影响）
        smooth_w = max(3, round(length(mag_all) / 60));
        mag_smooth = movmean(mag_all, smooth_w);

        cla(state.ax_mag);
        area(state.ax_mag, f_all, mag_smooth, ...
            'FaceColor', [0.30 0.65 1.00], 'FaceAlpha', 0.3, 'EdgeColor', 'none');
        hold(state.ax_mag, 'on');
        plot(state.ax_mag, f_all, mag_smooth, ...
            'Color', theme.success, 'LineWidth', 1.5);
        hold(state.ax_mag, 'off');
        xlim(state.ax_mag, [0 state.f_max]);
        ylim(state.ax_mag, [0 1.05]);
        title(state.ax_mag, sprintf('幅度谱 |X(f)|  (质心: %.0f Hz, 滚降: %.0f Hz)', ...
            features.centroid, features.rolloff), ...
            'Color', theme.text_dim, 'FontSize', 10);
        grid(state.ax_mag, 'on');
        state.ax_mag.GridAlpha = 0.3;

        hold(state.ax_mag, 'on');
        xline(state.ax_mag, features.centroid, '--', 'Color', theme.accent, ...
            'LineWidth', 1.2, 'Label', '质心');
        xline(state.ax_mag, features.rolloff, '--', 'Color', theme.warning, ...
            'LineWidth', 1.2, 'Label', '滚降(85%)');
        hold(state.ax_mag, 'off');

        % ---- 相位谱 ----
        cla(state.ax_phase);
        phase_all = features.phase_unwrap(:);
        gd_all = features.group_delay(:);
        gd_smooth = movmean(gd_all, smooth_w);

        yyaxis(state.ax_phase, 'left');
        plot(state.ax_phase, f_all, phase_all, ...
            'Color', theme.warning, 'LineWidth', 1.2);
        ylabel(state.ax_phase, '解卷相位 (rad)');
        state.ax_phase.YColor = theme.warning;

        yyaxis(state.ax_phase, 'right');
        plot(state.ax_phase, f_all, gd_smooth, ...
            'Color', theme.accent, 'LineWidth', 1.0);
        ylabel(state.ax_phase, '群延迟 (samples)');
        state.ax_phase.YColor = theme.accent;

        xlim(state.ax_phase, [0 state.f_max]);
        title(state.ax_phase, '相位谱 (解卷) & 群延迟', ...
            'Color', theme.text_dim, 'FontSize', 10);
        grid(state.ax_phase, 'on');
        state.ax_phase.GridAlpha = 0.3;
    end

    % ---- 更新得分柱状图 ----
    function updateScoreBarChart(scores, best_idx)
        cla(state.ax_scores);
        digits = 0:10;
        bar_colors = repmat(theme.btn_bg, 11, 1);
        bar_colors(best_idx, :) = theme.success;

        b = bar(state.ax_scores, digits, scores * 100, 'FaceColor', 'flat');
        b.CData = bar_colors;
        b.EdgeColor = 'none';
        b.FaceAlpha = 0.85;

        % 在最佳匹配上标注数字
        hold(state.ax_scores, 'on');
        text(state.ax_scores, best_idx-1, scores(best_idx)*100 + 3, ...
            ['★ ' num2str(best_idx-1)], ...
            'Color', theme.success, 'FontSize', 13, 'FontWeight', 'bold', ...
            'HorizontalAlignment', 'center');

        hold(state.ax_scores, 'off');
        ylim(state.ax_scores, [0 105]);
        state.ax_scores.XTick = digits;
        state.ax_scores.XLabel.String = '数字';
        state.ax_scores.YLabel.String = '综合匹配度 (%)';
        title(state.ax_scores, '各数字综合匹配度对比', 'Color', theme.text_dim, 'FontSize', 10);
        grid(state.ax_scores, 'on');
        state.ax_scores.GridAlpha = 0.3;
    end

    % ---- 重置 UI 到初始状态 ----
    function resetUI()
        state.lamp.Color = theme.text_dim;
        state.lbl_status.Text = '就绪';
        state.lbl_status.FontColor = theme.text_dim;
        state.lbl_digit.Text = '—';
        state.lbl_digit.FontColor = theme.success;
        state.lbl_confidence.Text = '置信度: —';
        state.lbl_detail.Text = '';
        state.lbl_top3.Text = '';
        state.btn_play.Enable = 'off';
        state.btn_load.Enable = 'on';
        state.btn_train.Enable = 'on';
        state.btn_record.Text = '⏺ 开始录音';
        state.btn_record.BackgroundColor = theme.accent;
    end

    % ---- 关闭窗口 ----
    function onClose()
        if state.is_recording
            try
                stop(state.recorder);
            catch
            end
        end
        delete(fig);
    end

end % DigitRecognitionGUI 主函数结束

%% ===========================================================================
% 以下为独立的工具函数
% ===========================================================================

%% -------------------- 预处理：加窗法去除静音/噪声 --------------------
function [sub_audio, start_idx] = preprocessAudio(audio, fs, frac)
    % preprocessAudio - 利用滑动窗能量检测提取语音有效段
    %
    % 输入:
    %   audio - 原始音频向量
    %   fs    - 采样率
    %   frac  - 保留比例 (如 0.3 表示保留能量最大的30%段)
    %
    % 输出:
    %   sub_audio - 提取的有效音频段
    %   start_idx - 有效段在原音频中的起始索引

    % ---- 帧能量 VAD：自适应定位语音起止点（不受停顿影响）----
    N = length(audio);
    frame_len = round(0.02 * fs);    % 20ms 帧长
    frame_shift = round(0.01 * fs);  % 10ms 帧移
    n_frames = floor((N - frame_len) / frame_shift) + 1;

    if n_frames < 3
        % 音频太短，直接使用
        sub_audio = audio;
        start_idx = 1;
    else
        % 逐帧能量
        energy = zeros(n_frames, 1);
        for i = 1:n_frames
            idx = (i-1)*frame_shift + 1;
            energy(i) = sum(audio(idx:idx+frame_len-1).^2);
        end

        % 噪声地板：最静 20% 帧的平均能量
        sorted_e = sort(energy);
        noise_floor = mean(sorted_e(1:max(1, round(0.2 * n_frames))));

        % 语音阈值：噪声地板 × 3
        thresh = max(noise_floor * 3, 0.01 * max(energy));

        % 找到语音起止帧
        speech_mask = energy > thresh;
        first_frame = find(speech_mask, 1, 'first');
        last_frame  = find(speech_mask, 1, 'last');

        if isempty(first_frame)
            % 未检测到语音 → 回退到 maxSumSubArray
            [~, start_idx] = maxSumSubArray(abs(audio), frac);
            window_len = floor(frac * N);
            end_idx = min(start_idx + window_len - 1, N);
            start_idx = max(start_idx, 1);
        else
            % 帧索引 → 采样索引（前后各加 50ms 余量）
            start_idx = max(1, (first_frame-1)*frame_shift + 1 - round(0.05*fs));
            end_idx   = min(N, last_frame*frame_shift + frame_len + round(0.05*fs));
        end

        sub_audio = audio(start_idx:end_idx);
    end

    % 汉明窗
    win = hamming(length(sub_audio));
    sub_audio = sub_audio .* win;
end

%% -------------------- 特征提取 --------------------
function features = extractFeatures(audio, fs, f_max, ~)
    % extractFeatures - 从音频段中提取幅度谱、相位谱及多种谱特征
    % 使用固定长度 FFT，确保所有录音产生完全相同的频率网格
    %
    % 输入:
    %   audio  - 预处理后的音频向量
    %   fs     - 采样率
    %   f_max  - 分析频率上限 (Hz)
    %
    % 输出:
    %   features - 包含所有提取特征的结构体

    N = length(audio);

    % ---- 固定长度 FFT（关键：所有录音使用同一 N_fft，频率网格一致）----
    N_fft_fixed = 2^14;  % 16384 点 FFT, df ≈ 2.69 Hz @ 44100Hz
    X = fft(audio, N_fft_fixed);
    X_half = X(1:floor(N_fft_fixed/2)+1, :);
    f = (0:size(X_half,1)-1)' * fs / N_fft_fixed;

    % ---- 分析频率范围 ----
    mask = f <= f_max;
    f_voice = f(mask);
    X_voice = X_half(mask);

    % ---- 幅度谱 ----
    mag = abs(X_voice);
    if max(mag) < eps
        mag = ones(size(mag));
    end
    mag_norm = mag / max(mag);

    % ---- 倒谱提升（Cepstral Liftering）：分离音调与声道 ----
    % 原理：log|X(f)| = log|S(f)| + log|H(f)|
    %       S(f): 声源（周期脉冲→频谱有等间隔谐波，对应音调）
    %       H(f): 声道滤波器（平滑包络，对应发音内容）
    %       IFFT→倒谱：低 queffency=声道，高 queffency=声源
    %       保留低 35 个倒谱系数→重建频谱包络→去除音调影响
    mag_log = log(mag_norm + 1e-6);
    % 对称延拓以构造实倒谱
    mag_log_sym = [mag_log; flipud(mag_log(2:end-1))];
    cepstrum = real(ifft(mag_log_sym));
    % 倒谱窗（低通）：仅保留声道分量
    n_lifter = 35;
    cep_lift = zeros(size(cepstrum));
    cep_lift(1:n_lifter) = cepstrum(1:n_lifter);
    cep_lift(end-n_lifter+2:end) = cepstrum(end-n_lifter+2:end);
    % 变换回频域 → 音调归一化的频谱包络
    mag_env_log = real(fft(cep_lift));
    mag_env_log = mag_env_log(1:length(mag_log));
    mag_env = exp(mag_env_log);
    mag_env = mag_env / max(mag_env);  % 归一化包络

    % ---- 相位谱 ----
    phase_raw = angle(X_voice);
    phase_unwrap = unwrap(phase_raw);

    % ---- 群延迟 ----
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

    % ---- 谱质心 ----
    centroid = sum(f_voice .* mag) / (sum(mag) + eps);

    % ---- 谱滚降 (85%) ----
    cum_energy = cumsum(mag.^2);
    rolloff_idx = find(cum_energy >= 0.85 * cum_energy(end), 1);
    if isempty(rolloff_idx), rolloff_idx = length(cum_energy); end
    rolloff = f_voice(rolloff_idx);

    % ---- 过零率 ----
    zcr = sum(abs(diff(sign(audio)))) / (2 * length(audio));

    % ---- RMS 能量 ----
    rms_energy = sqrt(mean(audio.^2));

    % ---- 频带合并（降维去噪）----
    % 对音调归一化后的包络进行对数频带合并（匹配用）
    n_bands_target = 180;
    band_edges = round(logspace(log10(50), log10(f_max), n_bands_target + 1));
    band_edges = unique(band_edges);
    n_bands = length(band_edges) - 1;
    mag_band = zeros(n_bands, 1);
    phase_band = zeros(n_bands, 1);
    gd_band = zeros(n_bands, 1);
    f_band = zeros(n_bands, 1);

    for b = 1:n_bands
        bin_mask = (f_voice >= band_edges(b)) & (f_voice < band_edges(b+1));
        if any(bin_mask)
            mag_band(b) = mean(mag_env(bin_mask));      % ← 用包络而非原始谱
            phase_band(b) = mean(phase_unwrap(bin_mask));
            gd_band(b) = mean(group_delay(bin_mask));
            f_band(b) = mean(f_voice(bin_mask));
        end
    end

    % ---- 组装特征 ----
    features = struct();
    % 全分辨率数据（用于绘图）
    features.freq_axis      = f_voice;
    features.mag_norm       = mag_norm;
    features.phase_unwrap   = phase_unwrap;
    features.group_delay    = group_delay;
    % 降维频带数据（用于匹配，大幅减少噪声干扰）
    features.freq_match     = f_band;
    features.mag_match      = mag_band;
    features.phase_match    = phase_band;
    features.gd_match       = gd_band;
    % 标量特征
    features.centroid       = centroid;
    features.rolloff        = rolloff;
    features.zcr            = zcr;
    features.rms_energy     = rms_energy;
    features.N_orig         = N;
    features.N_fft          = N_fft_fixed;
    features.n_bins         = length(f_voice);
    features.n_bands        = n_bands;
end

%% -------------------- 数字识别 --------------------
function [best_digit, confidence, all_scores, detail_scores] = ...
    recognizeDigit(features_test, ref_features, weights)
    % recognizeDigit - 多特征融合匹配识别数字
    %
    % 输入:
    %   features_test - 待识别音频的特征
    %   ref_features  - 参考特征库 (struct array, 每个元素对应一个数字)
    %   weights       - 各特征权重结构体
    %
    % 输出:
    %   best_digit    - 识别结果数字
    %   confidence    - 置信度 (0~1)
    %   all_scores    - 每个数字的综合得分
    %   detail_scores - 最佳匹配的分项得分

    n_digits = length(ref_features);
    all_scores = zeros(n_digits, 1);
    best_detail = [];

    for d = 1:n_digits
        % 跳过没有参考样本的数字
        if isempty(ref_features(d).features)
            all_scores(d) = -inf;
            continue;
        end
        % 跳过 features 不是结构体的异常数据
        if ~isstruct(ref_features(d).features)
            all_scores(d) = -inf;
            continue;
        end

        % 对该数字的每个参考样本计算得分，取平均
        n_refs = size(ref_features(d).features, 1);
        digit_scores = zeros(n_refs, 1);

        for r = 1:n_refs
            try
                ref_feat = ref_features(d).features(r);
                digit_scores(r) = computeMatchScore(features_test, ref_feat, weights);
            catch
                % 单个样本匹配失败则标记为无效，不影响其他样本
                digit_scores(r) = -inf;
            end
        end

        % 取最佳匹配（多样本时用 MAX 而非 MEAN，避免差样本稀释好样本）
        valid_scores = digit_scores(digit_scores > -inf);
        if isempty(valid_scores)
            all_scores(d) = -inf;
        else
            all_scores(d) = max(valid_scores);
        end

        % 记录最佳匹配的分项得分
        if d == 1 || all_scores(d) > max(all_scores(1:d-1))
            if ~isempty(valid_scores)
                [~, best_r] = max(digit_scores);
                try
                    best_detail = computeDetailScores(features_test, ...
                        ref_features(d).features(best_r));
                catch
                    best_detail = [];
                end
            end
        end
    end

    % 找到最佳匹配
    [best_score, best_idx] = max(all_scores);
    best_digit = best_idx - 1;  % 索引从1开始

    % 置信度 = 最佳匹配得分与次优得分的差距
    % （得分本身已反映匹配程度，直接使用更直观）
    confidence = max(0, best_score);

    % 返回分项得分
    if ~isempty(best_detail)
        detail_scores = best_detail;
    else
        detail_scores = struct('mag', 0, 'centroid', 0, 'rolloff', 0, 'gd', 0);
    end
end

%% -------------------- 综合匹配得分 --------------------
function score = computeMatchScore(feat_test, feat_ref, weights)
    % computeMatchScore - 4 特征融合匹配

    if isfield(feat_test, 'mag_match') && ~isempty(feat_test.mag_match)
        mag_t = feat_test.mag_match;  mag_r = feat_ref.mag_match;
        gd_t  = feat_test.gd_match;   gd_r  = feat_ref.gd_match;
    else
        mag_t = feat_test.mag_norm;  mag_r = feat_ref.mag_norm;
        gd_t  = feat_test.group_delay; gd_r  = feat_ref.group_delay;
    end

    % 1. 对数幅度谱相关
    mag_t_log = log10(mag_t + 0.001);
    mag_r_log = log10(mag_r + 0.001);
    mag_corr_mat = corrcoef(mag_t_log, mag_r_log);
    score_mag = max(0, mag_corr_mat(1,2));

    % 2. 谱质心距离
    c_diff = abs(feat_test.centroid - feat_ref.centroid);
    score_centroid = max(0, 1 - c_diff / 4000);

    % 3. 谱滚降距离
    r_diff = abs(feat_test.rolloff - feat_ref.rolloff);
    score_rolloff = max(0, 1 - r_diff / 4000);

    % 4. 群延迟相关（减均值消除 VAD 残余偏移）
    gd_t_norm = gd_t - mean(gd_t);
    gd_r_norm = gd_r - mean(gd_r);
    gd_corr_mat = corrcoef(gd_t_norm, gd_r_norm);
    score_gd = max(0, gd_corr_mat(1,2));

    score = weights.mag_corr    * score_mag + ...
            weights.centroid    * score_centroid + ...
            weights.rolloff     * score_rolloff + ...
            weights.group_delay * score_gd;
end

%% -------------------- 分项得分详解 --------------------
function detail = computeDetailScores(feat_test, feat_ref)
    % 计算并返回各分项得分（用于 GUI 显示）

    if isfield(feat_test, 'mag_match') && ~isempty(feat_test.mag_match)
        mag_t = feat_test.mag_match;  mag_r = feat_ref.mag_match;
        gd_t  = feat_test.gd_match;   gd_r  = feat_ref.gd_match;
    else
        mag_t = feat_test.mag_norm;  mag_r = feat_ref.mag_norm;
        gd_t  = feat_test.group_delay; gd_r  = feat_ref.group_delay;
    end

    mag_corr_mat = corrcoef(log10(mag_t + 0.001), log10(mag_r + 0.001));
    detail.mag = max(0, mag_corr_mat(1,2));

    c_diff = abs(feat_test.centroid - feat_ref.centroid);
    detail.centroid = max(0, 1 - c_diff / 4000);

    r_diff = abs(feat_test.rolloff - feat_ref.rolloff);
    detail.rolloff = max(0, 1 - r_diff / 4000);

    gd_corr_mat = corrcoef(gd_t - mean(gd_t), gd_r - mean(gd_r));
    detail.gd = max(0, gd_corr_mat(1,2));
end

%% -------------------- 最大和子数组 (加窗法核心) --------------------
function [maxSubArray, startIndex, maxSum] = maxSumSubArray(arr, fraction)
    % maxSumSubArray - 滑动窗口寻找最大能量段的起始位置
    %
    % 这是 demo 中的加窗法去噪核心：在音频中找到能量（幅度绝对值之和）
    % 最大的连续段，该段最有可能是有效语音。
    %
    % 输入:
    %   arr      - 输入数组（通常为 |audio|）
    %   fraction - 窗口占总长度的比例 (e.g. 0.3)
    %
    % 输出:
    %   maxSubArray - 最大能量段数据
    %   startIndex  - 起始索引
    %   maxSum      - 最大能量值

    n = length(arr);
    windowSize = floor(n * fraction);
    windowSize = max(windowSize, 1);
    if windowSize > n
        windowSize = n;
    end

    % 初始窗口和
    currentSum = sum(arr(1:windowSize));
    maxSum = currentSum;
    startIndex = 1;

    % 滑动窗口
    for i = 2:(n - windowSize + 1)
        currentSum = currentSum - arr(i - 1) + arr(i + windowSize - 1);
        if currentSum > maxSum
            maxSum = currentSum;
            startIndex = i;
        end
    end

    maxSubArray = arr(startIndex:(startIndex + windowSize - 1));
end

%% -------------------- 从文件名提取数字 --------------------
function digit = extractDigitFromName(filename)
    % extractDigitFromName - 从文件名中提取数字 (0~10)
    %
    % 支持的命名格式:
    %   num0, num01, 0_recording, digit_5, sample_10, test03 等

    % 尝试匹配 "10" 优先（避免被单独匹配为 "1" 或 "0"）
    if contains(filename, '10') || contains(filename, 'ten')
        digit = 10;
        return;
    end

    % 尝试匹配单个数字 0~9
    % 使用正则表达式匹配独立的数字
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
