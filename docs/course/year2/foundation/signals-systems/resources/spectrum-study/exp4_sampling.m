% 实验4：采样率变化对信号频谱的影响

clear; close all;

% 参数设置
f0 = 50;                    % 信号频率 50 Hz
T_duration = 0.23;          % 截取时长 230 ms（非整数周期，使泄漏可见）

fs_values = [150, 200, 300, 500, 1000, 2000, 5000];

% 绘图
n_fs = length(fs_values);
figure('Position', [100, 100, 1400, 1000]);

for i = 1:n_fs
    fs = fs_values(i);
    Ts = 1/fs;

    % 生成离散信号
    t = 0:Ts:T_duration-Ts;
    x = sin(2*pi * f0 * t);
    N = length(x);

    X = fft(x, N);
    X_mag = abs(X) / N;
    X_mag(2:N) = 2 * X_mag(2:N);

    f_axis = (0:N-1) * fs / N;
    half_idx = floor(N/2);

    % 左列：频谱
    subplot(n_fs, 2, 2*i-1);
    plot(f_axis(1:half_idx), X_mag(1:half_idx), 'b-', 'LineWidth', 1);
    hold on;
    xline(f0, 'r--', 'LineWidth', 0.8);
    xline(fs/2, 'g--', 'LineWidth', 0.8);  % 奈奎斯特频率
    xlabel('频率 (Hz)'); ylabel('幅值');
    title(sprintf('fs=%d Hz, N=%d, Δf=%.1f Hz', fs, N, fs/N));
    grid on;
    xlim([0, fs/2 * 1.1]);
    ylim([0, 1.2]);

    % 右列：时域采样点（只画前 40 ms）
    subplot(n_fs, 2, 2*i);
    t_show = t(t < 0.04);
    x_show = x(1:length(t_show));
    stem(t_show*1000, x_show, 'b.', 'MarkerSize', 4); hold on;
    plot(t_show*1000, x_show, 'b-', 'LineWidth', 0.5);
    xlabel('时间 (ms)'); ylabel('幅值');
    title(sprintf('fs=%d Hz 的采样点 (前40ms)', fs));
    grid on;
    ylim([-1.2, 1.2]);
end

sgtitle(sprintf(['实验4：采样率对频谱的影响\n' ...
    '固定信号 f_0=%dHz, 时长 T=%.0fms, 改变采样率'], ...
    f0, T_duration*1000), 'FontSize', 12);

saveas(gcf, 'figures/exp4_sampling.png');

% 输出数值对比
fprintf('\n  采样率变化影响总结 (f0=%dHz, T=%.0fms):\n', f0, T_duration*1000);
fprintf('  %-10s %-10s %-15s %-15s\n', 'fs(Hz)', 'N', 'Δf(Hz)', 'Nyquist(Hz)');
fprintf('  %s\n', repmat('-', 1, 55));
for i = 1:n_fs
    fs = fs_values(i);
    N = round(T_duration * fs);
    fprintf('  %-10d %-10d %-15.2f %-15d\n', fs, N, fs/N, fs/2);
end