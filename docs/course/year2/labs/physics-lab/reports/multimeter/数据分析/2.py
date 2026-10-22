import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 实验二数据 (电压表) ---
# X轴：测量值 (V测)
v_measured = np.array([0.95, 1.95, 2.90, 4.00, 5.00])
# Y轴：标准值 (V准)
v_standard = np.array([1.00, 2.00, 3.00, 4.00, 5.00])

# 计算误差 (V测 - V准)
v_diff = v_measured - v_standard

# 线性拟合
slope, intercept = np.polyfit(v_measured, v_standard, 1)

# 创建画布
fig = plt.figure(figsize=(8, 6), dpi=100)
ax1 = fig.add_subplot(111)

# --- 绘制主图 (左轴) ---
ax1.scatter(v_measured, v_standard, s=40, marker='x', color='blue')
lns1 = ax1.plot(v_measured, slope * v_measured + intercept, color='blue', linestyle='-', alpha=0.8, label='$V_{G} - V_{B}$ 拟合直线')

# 左轴设置
ax1.set_xlabel('$V_{G}$ / V (测量值)', fontsize=12)
ax1.set_ylabel('$V_{B}$ / V (标准值)', rotation=90, fontsize=12)
ax1.grid(which='major', linestyle=':', alpha=0.5)
ax1.set_xlim(0, 5.5)
ax1.set_ylim(0, 5.5)
ax1.set_title('附图2：5V量程电压表的校准曲线及误差分布', fontsize=14)

# --- 绘制副图 (右轴) ---
ax2 = ax1.twinx()

# 设置0轴位置
ax2.spines['bottom'].set_position(('data', 0))
ax2.spines['bottom'].set_color('red')
ax2.spines['bottom'].set_linestyle('--')
ax2.spines['bottom'].set_alpha(0.3)

# 绘制误差
ax2.scatter(v_measured, v_diff, s=30, marker='o', c='red', zorder=10)
lns2 = ax2.plot(v_measured, v_diff, 'r--', linewidth=1, label='绝对误差 $\Delta V$')

# 右轴设置
ax2.set_ylabel('$\Delta V = V_{G} - V_{B}$ / V', rotation=90, labelpad=10, fontsize=12, color='red')
# 根据你的误差范围 (-0.10 到 0)，设置合适的刻度
ax2.set_ylim(-0.2, 0.2)
ax2.tick_params(axis='y', colors='red')

# --- 合并图例 ---
lns = lns1 + lns2
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc='upper left', frameon=True)

plt.tight_layout()
plt.show()