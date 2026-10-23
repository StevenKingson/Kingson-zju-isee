% 实验1：正弦信号不同截取长度的频谱分析

clear; close all;

% 参数设置
fs = 1000;              % 采样率 1000 Hz
f0 = 50;                % 正弦信号频率 50 Hz
% 不同的截取长度（FFT 点数）
N_values = [32, 64, 128, 256, 512, 1024];

T_total = max(N_values) / fs * 1.1;  % 信号长度至少覆盖最大的 N
t = 0:1/fs:T_total-1/fs;
x = sin(2*pi*f0 * t);   % 原始正弦信号

% 绘图
figure('Position', [100, 100, 1200, 700]);

for i = 1:length(N_values)
    N = N_values(i);

    % 截取前 N 个点
    x_trunc = x(1:N);

    % 做 N 点 FFT
    X = fft(x_trunc, N);

    % 计算幅度谱
    X_mag = abs(X) / N;         % 归一化
    X_mag(2:N) = 2 * X_mag(2:N); % 单边谱（直流分量不乘2）

    % 频率轴
    f_axis = (0:N-1) * fs / N;

    % 只显示正频率部分
    half_idx = floor(N/2);

    subplot(2, 3, i);
    plot(f_axis(1:half_idx), X_mag(1:half_idx), 'LineWidth', 1.2);
    xlabel('频率 (Hz)', 'FontSize', 10);
    ylabel('幅值', 'FontSize', 10);
    grid on;

    delta_f = fs / N;
    title(sprintf('N = %d,  Δf = %.1f Hz', N, delta_f), 'FontSize', 11);
    xlim([0, 150]);
    ylim([0, 1.2]);

    % 标注理论峰值位置
    hold on;
    xline(f0, 'r--', 'LineWidth', 0.8);
    hold off;
end

sgtitle('实验1：不同截取长度的正弦信号频谱 (f_s=1000Hz, f_0=50Hz)', 'FontSize', 13);
saveas(gcf, 'figures/exp1_truncation.png');