import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 表1数据 - 基本磁化曲线
H = [23.26, 45.89, 54.51, 68.22, 81.55, 90.32, 103.29, 140.08, 219.60, 326.31]
B = [66.02, 131.05, 154.98, 194.03, 230.48, 256.94, 282.26, 322.58, 362.90, 383.06]
mu = [2.84, 2.86, 2.84, 2.84, 2.83, 2.84, 2.73, 2.30, 1.65, 1.17]

# 创建图形和主坐标轴
fig, ax1 = plt.subplots(figsize=(12, 8))

# 绘制B-H曲线
color_B = 'tab:red'
ax1.set_xlabel('$H$ (A/m)', fontsize=14, style='italic')
ax1.set_ylabel('$B$ (mT)', color=color_B, fontsize=14, style='italic')
line1 = ax1.plot(H, B, 'o-', color=color_B, linewidth=2, markersize=8, label='$B$-$H$ 曲线')
ax1.tick_params(axis='y', labelcolor=color_B)

# 标记每个数据点
for i, (h_val, b_val) in enumerate(zip(H, B)):
    ax1.annotate(f'{i+1}', (h_val, b_val), textcoords="offset points", 
                xytext=(5,5), ha='center', fontsize=9, color=color_B)

# 创建第二个Y轴
ax2 = ax1.twinx()
color_mu = 'tab:blue'
ax2.set_ylabel('$\mu$ ($10^{-3}$ H/m)', color=color_mu, fontsize=14, style='italic')
line2 = ax2.plot(H, mu, 's-', color=color_mu, linewidth=2, markersize=6, label='$\mu$-$H$ 曲线')
ax2.tick_params(axis='y', labelcolor=color_mu)

# 标记每个数据点
for i, (h_val, mu_val) in enumerate(zip(H, mu)):
    ax2.annotate(f'{i+1}', (h_val, mu_val), textcoords="offset points", 
                xytext=(-5,-10), ha='center', fontsize=9, color=color_mu)

# 添加网格和图例
ax1.grid(True, alpha=0.3)
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper right', fontsize=12)

plt.title('磁化曲线: $B$-$H$ 和 $\mu$-$H$', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

# 打印数据验证
print("数据验证:")
print("H (A/m)\t\tB (mT)\t\tμ (10^-3 H/m)")
for i in range(len(H)):
    print(f"{H[i]:.2f}\t\t{B[i]:.2f}\t\t{mu[i]:.2f}")