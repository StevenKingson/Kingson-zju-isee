% 实验5：整周期截取 vs 非整周期截取

clear; close all;

% 参数设置
fs = 1000;                  % 采样率
f0 = 50;                    % 信号频率
% 每周期采样点数 = fs/f0 = 20 个点/周期

T_period = 1/f0;            % 信号周期 = 0.02 s = 20 ms
points_per_period = fs / f0; % = 20

% 整周期截取：N 为 20 的倍数
N_int = [20, 40, 100, 200];
% 对应的完整周期数：[1, 2, 5, 10]

% 非整周期截取：N 不是 20 的倍数
N_nonint = [25, 55, 95, 155];
% 对应的周期数：[1.25, 2.75, 4.75, 7.75]

% 绘图
figure('Position', [100, 100, 1600, 800]);

% 上半部分：整周期截取
for i = 1:4
    N = N_int(i);
    t = (0:N-1)' / fs;
    x = sin(2*pi * f0 * t);

    X = fft(x, N);
    X_db = 20 * log10(abs(X(1:N/2)) / max(abs(X(1:N/2))) + 1e-15);
    f_axis = (0:N/2-1) * fs / N;

    subplot(2, 4, i);
    stem(f_axis, X_db, '.', 'MarkerSize', 6, 'Color', 'b');
    hold on;
    xline(f0, 'r-', 'LineWidth', 1.5);
    xlabel('频率 (Hz)'); ylabel('幅值 (dB)');
    num_periods = N / points_per_period;
    title(sprintf('整周期 N=%d (%.1f个周期)', N, num_periods));
    grid on;
    xlim([0, 150]); ylim([-60, 5]);
end

% 下半部分：非整周期截取
for i = 1:4
    N = N_nonint(i);
    t = (0:N-1)' / fs;
    x = sin(2*pi * f0 * t);

    X = fft(x, N);
    X_db = 20 * log10(abs(X(1:N/2)) / max(abs(X(1:N/2))) + 1e-15);
    f_axis = (0:N/2-1) * fs / N;

    subplot(2, 4, i+4);
    stem(f_axis, X_db, '.', 'MarkerSize', 6, 'Color', 'r');
    hold on;
    xline(f0, 'r-', 'LineWidth', 1.5);
    xlabel('频率 (Hz)'); ylabel('幅值 (dB)');
    num_periods = N / points_per_period;
    title(sprintf('非整周期 N=%d (%.2f个周期)', N, num_periods));
    grid on;
    xlim([0, 150]); ylim([-60, 5]);
end

sgtitle(sprintf(['实验5：整周期 vs 非整周期截取\n' ...
    'f_s=%dHz, f_0=%dHz, 每周期%d个采样点'], ...
    fs, f0, points_per_period), 'FontSize', 13);

saveas(gcf, 'figures/exp5_period.png');

% 额外对比：相同数据长度，加窗改善
figure('Position', [100, 100, 1000, 500]);

N = 95;  % 非整周期
t = (0:N-1)' / fs;
x = sin(2*pi * f0 * t);

% 不加窗
X_rect = fft(x, N);
X_rect_db = 20 * log10(abs(X_rect(1:N/2)) / max(abs(X_rect(1:N/2))) + 1e-15);

% 加汉明窗
x_hamm = x .* hamming(N);
X_hamm = fft(x_hamm, N);
X_hamm_db = 20 * log10(abs(X_hamm(1:N/2)) / max(abs(X_hamm(1:N/2))) + 1e-15);

f_axis = (0:N/2-1) * fs / N;

subplot(1, 2, 1);
stem(f_axis, X_rect_db, '.', 'MarkerSize', 6); hold on;
xline(f0, 'r-', 'LineWidth', 1);
title(sprintf('矩形窗 (非整周期 N=%d)', N));
xlabel('频率 (Hz)'); ylabel('幅值 (dB)');
grid on; xlim([0, 150]); ylim([-60, 5]);

subplot(1, 2, 2);
stem(f_axis, X_hamm_db, '.', 'MarkerSize', 6); hold on;
xline(f0, 'r-', 'LineWidth', 1);
title(sprintf('汉明窗 (非整周期 N=%d)', N));
xlabel('频率 (Hz)'); ylabel('幅值 (dB)');
grid on; xlim([0, 150]); ylim([-60, 5]);

sgtitle('实验5补充：加窗对非整周期截取泄漏的改善', 'FontSize', 12);
saveas(gcf, 'figures/exp5_windowing_fix.png');