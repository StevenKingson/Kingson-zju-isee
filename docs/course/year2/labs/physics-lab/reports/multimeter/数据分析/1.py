import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体 (如果你本地有'DingTalk JinBuTi'可直接用，否则建议用'SimHei'黑体)
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False 

# --- 实验一数据 (电流表) ---
# X轴：测量值 (I测)
i_measured = np.array([1.00, 2.05, 3.05, 4.10, 4.95])
# Y轴：标准值 (I准)
i_standard = np.array([1.00, 2.00, 3.00, 4.00, 5.00])

# 计算误差 (I测 - I准)
i_diff = i_measured - i_standard

# 线性拟合 (拟合 I测 和 I准 的关系)
slope, intercept = np.polyfit(i_measured, i_standard, 1)

# 创建画布
fig = plt.figure(figsize=(8, 6), dpi=100)
ax1 = fig.add_subplot(111)

# --- 绘制主图 (左轴：校准曲线) ---
# 1. 散点
ax1.scatter(i_measured, i_standard, s=40, marker='x', color='blue', label='实验数据点', zorder=5)
# 2. 拟合线
lns1 = ax1.plot(i_measured, slope * i_measured + intercept, color='blue', linestyle='-', alpha=0.8, label='$I_{G} - I_{B}$ 拟合直线')

# 设置左轴标签和范围
ax1.set_xlabel('$I_{G}$ / mA (测量值)', fontsize=12)
ax1.set_ylabel('$I_{B}$ / mA (标准值)', rotation=90, fontsize=12)
ax1.grid(which='major', linestyle=':', alpha=0.5)
ax1.set_xlim(0, 5.5)
ax1.set_ylim(0, 5.5)
ax1.set_title('附图1：5mA量程电流表的校准曲线及误差分布', fontsize=14)

# --- 绘制副图 (右轴：误差 ΔI) ---
ax2 = ax1.twinx()

# 绘制误差散点和连线
# 移动脊柱(spine)使得0轴在中间
ax2.spines['right'].set_visible(True)
ax2.spines['bottom'].set_position(('data', 0)) # 将x轴脊柱移动到y=0处
ax2.spines['top'].set_visible(False)
# 为了不遮挡左轴数据，去掉原来的底边框显示，只保留0线效果
ax2.spines['bottom'].set_linestyle('--')
ax2.spines['bottom'].set_alpha(0.3)
ax2.spines['bottom'].set_color('red')

# 绘制误差数据
ax2.scatter(i_measured, i_diff, s=30, marker='o', c='red', zorder=10)
lns2 = ax2.plot(i_measured, i_diff, 'r--', linewidth=1, label='绝对误差 $\Delta I$')

# 设置右轴标签和范围
ax2.set_ylabel('$\Delta I = I_{G} - I_{B}$ / mA', rotation=90, labelpad=10, fontsize=12, color='red')
# 根据你的误差范围 (-0.05 到 0.10)，设置合适的刻度
ax2.set_ylim(-0.20, 0.20) 
ax2.tick_params(axis='y', colors='red')

# --- 合并图例 ---
lns = lns1 + lns2
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc='upper left', frameon=True)

plt.tight_layout()
plt.show()