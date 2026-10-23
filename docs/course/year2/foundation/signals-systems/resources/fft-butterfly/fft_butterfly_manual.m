clear; clc; close all;

%% 1. 主函数：手动蝶形 FFT

function X = my_fft_dit2(x)
    % 确保输入为行向量
    is_col = iscolumn(x);
    x = x(:).';  % 转为行向量便于处理

    N = length(x);

    % 检查 N 是否为 2 的幂
    if bitand(N, N-1) ~= 0
        error('输入长度 N 必须为 2 的幂。当前 N = %d', N);
    end

    num_bits = log2(N);

    %% 步骤 1: 位反转重排 (Bit-Reversal Permutation)
    % 目的：将输入数据按位反转顺序重新排列，以便后续蝶形运算可以原位进行
    X = x;  % 复制输入，后续在原位计算
    for i = 0:N-1
        % 位反转：将 i 的二进制表示反转
        rev_i = bit_reverse(i, num_bits);

        % 只交换一次（当 i < rev_i 时交换，避免重复）
        if i < rev_i
            % MATLAB 索引从 1 开始
            tmp = X(i + 1);
            X(i + 1) = X(rev_i + 1);
            X(rev_i + 1) = tmp;
        end
    end

    %% 步骤 2: 逐级蝶形运算
    % 共 log2(N) 级，每级处理不同大小的蝶形
    for stage = 1:num_bits
        sub_dft_len = 2^stage;       % 当前级每个子 DFT 的长度
        half_len    = sub_dft_len / 2; % 蝶形跨度（上下支路的距离）

        % 对当前级的所有旋转因子组
        for k = 0:half_len-1
            % ---- 计算旋转因子 W_N^k = exp(-1j * 2*pi*k / sub_dft_len) ----
            W = exp(-1j * 2 * pi * k / sub_dft_len);

            % 对当前旋转因子覆盖的所有蝶形对
            for start_idx = k : sub_dft_len : N-1
                top    = start_idx + 1;           % 上位位置 (MATLAB 1-indexed)
                bottom = start_idx + half_len + 1; % 下位位置

                % ====== 蝶形运算核心 ======
                %  temp     = W * X(bottom)
                %  X(bottom) = X(top) - temp   (下支路：差值)
                %  X(top)    = X(top) + temp   (上支路：和值)
                temp = W * X(bottom);

                X_bottom_new = X(top) - temp;
                X_top_new    = X(top) + temp;

                X(top)    = X_top_new;
                X(bottom) = X_bottom_new;
            end
        end
    end

    % 恢复原始维度
    if is_col
        X = X(:);
    end
end

%% 2. 辅助函数：位反转

function rev = bit_reverse(n, num_bits)
    rev = 0;
    for bit = 0:num_bits-1
        if bitand(n, bitshift(1, bit))
            rev = bitor(rev, bitshift(1, num_bits - 1 - bit));
        end
    end
end

%% 3. 手动蝶形 IFFT

function y = my_ifft_dit2(X)
    N = length(X);
    y = conj(my_fft_dit2(conj(X))) / N;
end

%% 4. 可视化蝶形数据流图

function plot_butterfly_diagram(N)
    figure('Name', sprintf('FFT 蝶形数据流图 (N=%d)', N), 'NumberTitle', 'off');
    hold on;
    title(sprintf('基-2 DIT FFT 蝶形数据流图 (N = %d)', N), 'FontSize', 14);
    axis off;

    num_bits = log2(N);

    % 每级之间的水平间距
    dx = 2;
    % 节点之间的垂直间距
    dy = 1;

    % 存储节点位置 (列号, 行号)
    % node_pos(stage+1, node_index) = [x, y]，stage 从 0(输入) 到 num_bits(输出)
    node_pos = cell(num_bits + 1, N);

    % 输入节点位置（stage 0）
    for i = 0:N-1
        rev_i = bit_reverse(i, num_bits);
        node_pos{1, i+1} = [0, -(N-1-rev_i)*dy];
    end

    % 各阶段节点位置
    for stage = 1:num_bits
        for i = 0:N-1
            node_pos{stage+1, i+1} = [stage*dx, -(N-1-i)*dy];
        end
    end

    % 绘制节点和连线
    for stage = 1:num_bits
        sub_dft_len = 2^stage;
        half_len = sub_dft_len / 2;

        for k = 0:half_len-1
            for start_idx = k : sub_dft_len : N-1
                top_idx    = start_idx;
                bottom_idx = start_idx + half_len;

                % 上一级的节点位置
                prev_top    = node_pos{stage, top_idx+1};
                prev_bottom = node_pos{stage, bottom_idx+1};

                % 当前级的节点位置
                curr_top    = node_pos{stage+1, top_idx+1};
                curr_bottom = node_pos{stage+1, bottom_idx+1};

                % 画连线：上和
                plot([prev_top(1), curr_top(1)], [prev_top(2), curr_top(2)], ...
                     'b-', 'LineWidth', 1);
                % 画连线：上到下
                plot([prev_top(1), curr_bottom(1)], [prev_top(2), curr_bottom(2)], ...
                     'b-', 'LineWidth', 1);
                % 画连线：下到上（经过旋转因子）
                plot([prev_bottom(1), curr_top(1)], [prev_bottom(2), curr_top(2)], ...
                     'r--', 'LineWidth', 1);
                % 画连线：下和下
                plot([prev_bottom(1), curr_bottom(1)], [prev_bottom(2), curr_bottom(2)], ...
                     'r--', 'LineWidth', 1);

                % 标注旋转因子
                mid_x = (prev_bottom(1) + curr_top(1)) / 2 + 0.3;
                mid_y = (prev_bottom(2) + curr_top(2)) / 2;
                text(mid_x, mid_y, sprintf('W_%d^{%d}', sub_dft_len, k), ...
                     'FontSize', 8, 'Color', 'r');
            end
        end
    end

    % 绘制节点圆圈
    for stage = 0:num_bits
        for i = 0:N-1
            pos = node_pos{stage+1, i+1};
            plot(pos(1), pos(2), 'ko', 'MarkerSize', 6, 'MarkerFaceColor', 'w');
            if stage == 0
                text(pos(1)-0.5, pos(2), sprintf('x[%d]', i), ...
                     'FontSize', 9, 'HorizontalAlignment', 'right');
            elseif stage == num_bits
                text(pos(1)+0.5, pos(2), sprintf('X[%d]', i), ...
                     'FontSize', 9, 'HorizontalAlignment', 'left');
            end
        end
    end

    % 标注级数
    for stage = 0:num_bits
        if stage == 0
            text(stage*dx, (N-1)*dy/2 + 1, '输入\n(位反转后)', ...
                 'FontSize', 10, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
        elseif stage == num_bits
            text(stage*dx, (N-1)*dy/2 + 1, '输出', ...
                 'FontSize', 10, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
        else
            text(stage*dx, (N-1)*dy/2 + 1.5, sprintf('第 %d 级', stage), ...
                 'FontSize', 10, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
        end
    end

    hold off;
end

%% 5. 测试与验证

fprintf('=============================================================\n');
fprintf('     基于蝶形运算的基-2 DIT FFT 手动实现 — 测试与验证\n');
fprintf('=============================================================\n\n');

%% 测试 1: 单频正弦信号
fprintf('【测试 1】单频正弦信号: x[n] = sin(2π·50·n/fs)\n');
fs = 256;           % 采样率
N1 = 256;           % FFT 点数 (2^8)
t1 = (0:N1-1) / fs;
f_sig = 50;         % 信号频率
x1 = sin(2 * pi * f_sig * t1);

% 手动 FFT
X1_manual = my_fft_dit2(x1);
% MATLAB 内置 FFT
X1_builtin = fft(x1);

% 比较
err1 = max(abs(X1_manual - X1_builtin));
fprintf('  最大绝对误差: %.2e\n', err1);

% 绘图
figure('Name', '测试1：单频正弦信号', 'NumberTitle', 'off');

subplot(2,2,1);
plot(t1(1:min(64,end)), x1(1:min(64,end)), 'b-', 'LineWidth', 1.2);
xlabel('时间 (s)'); ylabel('幅度');
title('时域信号 (前64点)'); grid on;

freq1 = (0:N1-1) * fs / N1;
subplot(2,2,2);
plot(freq1(1:N1/2), abs(X1_manual(1:N1/2)), 'b-', 'LineWidth', 1.2);
xlabel('频率 (Hz)'); ylabel('|X[k]|');
title('手动FFT — 幅度谱'); grid on;
xline(f_sig, 'r--', sprintf('f=%dHz', f_sig));

subplot(2,2,3);
plot(freq1(1:N1/2), abs(X1_builtin(1:N1/2)), 'r-', 'LineWidth', 1.2);
xlabel('频率 (Hz)'); ylabel('|X[k]|');
title('MATLAB内置FFT — 幅度谱'); grid on;

subplot(2,2,4);
plot(freq1(1:N1/2), abs(X1_manual(1:N1/2)) - abs(X1_builtin(1:N1/2)), 'k-', 'LineWidth', 1.2);
xlabel('频率 (Hz)'); ylabel('差值');
title('幅度谱差异'); grid on;

sgtitle('测试1：单频正弦信号 — 手动FFT vs 内置FFT');

%% 测试 2: 多频叠加信号
fprintf('\n【测试 2】多频叠加信号: x[n] = sin + cos + 0.5*sin\n');
N2 = 512;
t2 = (0:N2-1) / 1000;
x2 = sin(2*pi*50*t2) + cos(2*pi*120*t2) + 0.5*sin(2*pi*200*t2);

X2_manual = my_fft_dit2(x2);
X2_builtin = fft(x2);
err2 = max(abs(X2_manual - X2_builtin));
fprintf('  最大绝对误差: %.2e\n', err2);

figure('Name', '测试2：多频叠加信号', 'NumberTitle', 'off');

subplot(2,1,1);
plot(t2(1:200), x2(1:200), 'b-', 'LineWidth', 1);
xlabel('时间 (s)'); ylabel('幅度');
title('时域信号 (前200点)'); grid on;

freq2 = (0:N2-1) * 1000 / N2;
subplot(2,1,2);
plot(freq2(1:N2/2), abs(X2_manual(1:N2/2)), 'b-', 'LineWidth', 1.2);
hold on;
plot(freq2(1:N2/2), abs(X2_builtin(1:N2/2)), 'r--', 'LineWidth', 1);
xlabel('频率 (Hz)'); ylabel('|X[k]|');
title('幅度谱对比 (蓝:手动, 红:内置)'); grid on;
xline([50, 120, 200], 'k--', {'50Hz','120Hz','200Hz'});
legend('手动FFT', '内置FFT', 'Location', 'best');

sgtitle('测试2：多频叠加信号验证');

%% 测试 3: 矩形脉冲（验证频谱形状）
fprintf('\n【测试 3】矩形脉冲信号\n');
N3 = 256;
x3 = [ones(1, 32), zeros(1, N3-32)];  % 宽度32的矩形脉冲

X3_manual = my_fft_dit2(x3);
X3_builtin = fft(x3);
err3 = max(abs(X3_manual - X3_builtin));
fprintf('  最大绝对误差: %.2e\n', err3);

figure('Name', '测试3：矩形脉冲', 'NumberTitle', 'off');

subplot(2,2,1);
stem(0:N3-1, x3, 'b.', 'MarkerSize', 4);
xlabel('n'); ylabel('x[n]');
title('矩形脉冲 (宽度=32)'); grid on;
xlim([0, N3-1]);

subplot(2,2,2);
freq3 = (0:N3-1) / N3;
plot(freq3, abs(X3_manual), 'b-', 'LineWidth', 1.2);
xlabel('归一化频率'); ylabel('|X[k]|');
title('手动FFT幅度谱'); grid on;

subplot(2,2,3);
plot(freq3, angle(X3_manual), 'b-', 'LineWidth', 1);
xlabel('归一化频率'); ylabel('相位 (rad)');
title('手动FFT相位谱'); grid on;

subplot(2,2,4);
plot(freq3, abs(X3_manual) - abs(X3_builtin), 'k-', 'LineWidth', 1.2);
xlabel('归一化频率'); ylabel('差值');
title('与内置FFT幅度谱差异'); grid on;

sgtitle('测试3：矩形脉冲信号验证');

%% 测试 4: IFFT 验证（正变换+逆变换 = 原始信号）
fprintf('\n【测试 4】正变换 → 逆变换 还原验证\n');
N4 = 128;
x4 = randn(1, N4) + 1j * randn(1, N4) * 0.5;  % 复数随机信号

X4 = my_fft_dit2(x4);       % 正变换
x4_recovered = my_ifft_dit2(X4);  % 逆变换

err4 = max(abs(x4 - x4_recovered));
fprintf('  正变换→逆变换 最大还原误差: %.2e\n', err4);

%% 测试 5: 不同 N 值的精度测试
fprintf('\n【测试 5】不同 N 值的精度测试\n');
N_values = [8, 16, 32, 64, 128, 256, 512, 1024];
fprintf('  %6s  %12s\n', 'N', '最大误差');
fprintf('  ------  ------------\n');
for n_val = N_values
    x_test = randn(1, n_val);
    X_man = my_fft_dit2(x_test);
    X_builtin = fft(x_test);
    err = max(abs(X_man - X_builtin));
    fprintf('  %6d  %12.2e\n', n_val, err);
end

%% 测试 6: 蝶形数据流图绘制 (N=8)
fprintf('\n【测试 6】绘制蝶形数据流图 (N=8)\n');
plot_butterfly_diagram(8);

%% 测试 7: 性能对比
fprintf('\n【测试 7】性能对比 (N=4096)\n');
N_perf = 4096;
x_perf = randn(1, N_perf) + 1j * randn(1, N_perf);

% 手动实现
tic;
X_man_perf = my_fft_dit2(x_perf);
t_manual = toc;

% MATLAB 内置
tic;
X_builtin_perf = fft(x_perf);
t_builtin = toc;

fprintf('  手动蝶形FFT耗时: %.4f 秒\n', t_manual);
fprintf('  MATLAB内置FFT耗时: %.4f 秒\n', t_builtin);
fprintf('  误差: %.2e\n', max(abs(X_man_perf - X_builtin_perf)));
fprintf('  (MATLAB内置FFT使用高度优化的FFTW库，速度更快属正常)\n');

%% 6. 逐级蝶形过程详细演示 (N=8)

fprintf('\n=============================================================\n');
fprintf('     N=8 逐级蝶形运算过程演示\n');
fprintf('=============================================================\n\n');

x_demo = [1, 2, 3, 4, 5, 6, 7, 8];
fprintf('输入序列 x[n]: ');
fprintf('%d  ', x_demo);
fprintf('\n\n');

% ---- 位反转 ----
num_bits_demo = 3;  % log2(8)
X_demo = x_demo;
fprintf('--- 位反转重排 ---\n');
for i = 0:7
    rev_i = bit_reverse(i, num_bits_demo);
    if i < rev_i
        tmp = X_demo(i+1);
        X_demo(i+1) = X_demo(rev_i+1);
        X_demo(rev_i+1) = tmp;
        fprintf('  交换 x[%d] ↔ x[%d]\n', i, rev_i);
    end
end
fprintf('位反转后: ');
fprintf('%.1f  ', X_demo);
fprintf('\n\n');

% ---- 逐级蝶形 ----
for stage = 1:num_bits_demo
    sub_dft_len = 2^stage;
    half_len = sub_dft_len / 2;
    fprintf('--- 第 %d 级 (子DFT长度=%d, 跨度=%d) ---\n', stage, sub_dft_len, half_len);

    for k = 0:half_len-1
        W = exp(-1j * 2 * pi * k / sub_dft_len);
        fprintf('  旋转因子 W_%d^%d = %.3f + j(%.3f)\n', ...
                sub_dft_len, k, real(W), imag(W));

        for start_idx = k : sub_dft_len : 7
            top = start_idx + 1;
            bottom = start_idx + half_len + 1;
            fprintf('    蝶形对: x[%d], x[%d] → ', start_idx, start_idx+half_len);

            temp = W * X_demo(bottom);
            X_bot_new = X_demo(top) - temp;
            X_top_new = X_demo(top) + temp;

            X_demo(top) = X_top_new;
            X_demo(bottom) = X_bot_new;
            fprintf('x[%d]=%.3f%+.3fj, x[%d]=%.3f%+.3fj\n', ...
                    start_idx, real(X_top_new), imag(X_top_new), ...
                    start_idx+half_len, real(X_bot_new), imag(X_bot_new));
        end
    end
    fprintf('  第 %d 级结果: ', stage);
    fprintf('%.2f%+.2fj  ', [real(X_demo); imag(X_demo)]);
    fprintf('\n\n');
end

% 与 MATLAB 内置对比
X_builtin_demo = fft(x_demo);
fprintf('手动FFT结果:    ');
fprintf('%.2f%+.2fj  ', [real(X_demo); imag(X_demo)]);
fprintf('\n');
fprintf('MATLAB内置FFT:  ');
fprintf('%.2f%+.2fj  ', [real(X_builtin_demo); imag(X_builtin_demo)]);
fprintf('\n');
fprintf('差异:           ');
fprintf('%.2e       ', abs(X_demo - X_builtin_demo));
fprintf('\n\n');

%% 7. 复杂度验证

fprintf('=============================================================\n');
fprintf('     复杂度验证\n');
fprintf('=============================================================\n\n');

% 计算复数乘法的理论值 vs 实际运算次数
% 蝶形FFT的复数乘法次数 = (N/2) * log2(N)
fprintf('理论复数乘法次数 (N/2)*log2(N):\n');
for n_val = [8, 16, 32, 64, 128, 256, 512, 1024]
    mult_theory = (n_val/2) * log2(n_val);
    add_theory  = n_val * log2(n_val);
    fprintf('  N=%4d: 乘法=%6.0f  加法=%6.0f   直接DFT乘法=%7.0f\n', ...
            n_val, mult_theory, add_theory, n_val^2);
end
fprintf('\n');

fprintf('=========================== 测试完成 ===========================\n');
