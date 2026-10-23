% 实验2：不同窗函数的频谱效果对比

clear; close all;

% 参数设置
fs = 1000;
f0 = 50;
N = 128;                    % N 较小，窗函数差异明显
t = (0:N-1)' / fs;
x = sin(2*pi * f0 * t);

% 定义窗函数
win_types = {'矩形窗', '汉明窗', '汉宁窗', '布莱克曼窗'};
win_colors = {'b', 'r', 'g', 'm'};

% 生成四种窗
wins = cell(4, 1);
wins{1} = rectwin(N);
wins{2} = hamming(N);
wins{3} = hann(N);
wins{4} = blackman(N);

% 绘图
figure('Position', [100, 100, 1100, 750]);

% 子图1：时域波形（上方，占满宽）
subplot(2, 2, [1, 2]);
plot(t*1000, x, 'k-', 'LineWidth', 0.5); hold on;
legend_entries = {'原始信号'};

for i = 1:4
    plot(t*1000, x .* wins{i}, win_colors{i}, 'LineWidth', 1);
    legend_entries{end+1} = win_types{i};
end

xlabel('时间 (ms)'); ylabel('幅值');
title('加窗后的时域信号');
legend(legend_entries, 'Location', 'northeast');
grid on;

% 子图2：频谱（线性坐标，左下）
subplot(2, 2, 3);
f_axis = (0:N/2-1) * fs / N;

for i = 1:4
    x_win = x .* wins{i};
    X = fft(x_win, N);
    X_mag = abs(X(1:N/2)) / N * 2;
    plot(f_axis, X_mag, win_colors{i}, 'LineWidth', 1.2); hold on;
end

xline(f0, 'k--', 'LineWidth', 0.8);
xlabel('频率 (Hz)'); ylabel('幅值');
title('频谱对比（线性坐标）'); legend(win_types, 'Location', 'northeast');
grid on; xlim([0, 150]);

% 子图3：频谱（dB坐标，右下）
subplot(2, 2, 4);

for i = 1:4
    x_win = x .* wins{i};
    X = fft(x_win, N);
    X_db = 20 * log10(abs(X(1:N/2)) / max(abs(X(1:N/2))) + eps);
    plot(f_axis, X_db, win_colors{i}, 'LineWidth', 1.2); hold on;
end

xline(f0, 'k--', 'LineWidth', 0.8);
xlabel('频率 (Hz)'); ylabel('幅值 (dB)');
title('频谱对比（dB坐标）'); legend(win_types, 'Location', 'northeast');
grid on; xlim([0, 150]); ylim([-80, 5]);

sgtitle(sprintf('实验2：不同窗函数的频谱效果对比 (N=%d, f_s=%dHz, f_0=%dHz)', N, fs, f0), 'FontSize', 12);

saveas(gcf, 'figures/exp2_windows.png');

% 输出数值对比
fprintf('\n  窗函数旁瓣高度对比 (N=%d):\n', N);
fprintf('  %-18s %s\n', '窗函数', '第一旁瓣高度(dB)');
fprintf('  %-18s %s\n', '------------------', '----------------');
for i = 1:4
    x_win = x .* wins{i};
    X = fft(x_win, 4096);  % 高分辨率看旁瓣
    X_db = 20 * log10(abs(X(1:2048)) / max(abs(X(1:2048))) + eps);
    [~, peak_idx] = max(X_db);
    for k = peak_idx+10:length(X_db)-1
        if X_db(k) > X_db(k-1) && X_db(k) > X_db(k+1) && X_db(k) > -80
            fprintf('  %-18s %.1f dB\n', win_types{i}, X_db(k));
            break;
        end
    end
end
