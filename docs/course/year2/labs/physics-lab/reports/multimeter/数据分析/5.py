import matplotlib.pyplot as plt
import numpy as np

# 设置字体
plt.rcParams['font.sans-serif'] = ['SimHei'] # 若报错可改为 'Arial Unicode MS' 或 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False

# --- 1. 数据准备 ---
# Rx 阻值
Rx = np.array([0, 100, 200, 500, 1000, 1500, 2000, 3000, 5000, 10000]) # 去掉30k和无穷大以便绘图清晰
# 实验读取值 (归一化/刻度值)
I_read = np.array([1.00, 0.74, 0.60, 0.36, 0.22, 0.15, 0.11, 0.07, 0.04, 0.01])
# 实际电流值 (还原为5mA量程)
I_real = I_read * 5 

# 理论计算参数
E0 = 1.5  # V
R_total = 300 # Ohm
# 生成平滑理论曲线数据
Rx_smooth = np.linspace(0, 10500, 500)
I_theory_smooth = (E0 / (R_total + Rx_smooth)) * 1000 # 换算为mA

# 计算对应离散点的理论值以便算误差
I_theory_points = (E0 / (R_total + Rx)) * 1000
# 绝对误差
I_error = I_real - I_theory_points

# --- 2. 绘图 (双子图布局) ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8), dpi=100, sharex=True, gridspec_kw={'height_ratios': [3, 1]})

# --- 上图：特性曲线对比 ---
# 绘制理论曲线
ax1.plot(Rx_smooth, I_theory_smooth, color='#1f77b4', linewidth=2, label='理论计算曲线 ($E=1.5V, R_{内}=300\Omega$)')
# 绘制实验散点
ax1.scatter(Rx, I_real, color='#d62728', s=50, zorder=5, marker='o', label='实验测量数据 (修正量程后)')

# 标注关键点 (中值电阻)
ax1.annotate(f'中值电阻 $300\Omega$\n$I=2.5mA$', xy=(300, 2.5), xytext=(1500, 3.5),
             arrowprops=dict(facecolor='black', shrink=0.05), fontsize=10)

ax1.set_ylabel('表头电流 $I$ / mA', fontsize=12)
ax1.set_title('实验三：欧姆表改装 $I-R_x$ 特性及误差分析', fontsize=14)
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(fontsize=10)
ax1.set_ylim(-0.2, 5.5)

# --- 下图：绝对误差分布 ---
ax2.plot(Rx, I_error, color='#2ca02c', marker='s', linestyle='--', linewidth=1.5, label='绝对误差 $\Delta I = I_{实} - I_{理}$')
ax2.axhline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5) # 0误差参考线

ax2.set_ylabel('误差 $\Delta I$ / mA', fontsize=12)
ax2.set_xlabel('待测电阻 $R_x$ / $\Omega$', fontsize=12)
ax2.grid(True, linestyle=':', alpha=0.5)
ax2.legend(fontsize=10)
ax2.set_ylim(-0.3, 0.3)

# 在误差图中标记数值
for x, y in zip(Rx, I_error):
    ax2.text(x, y + 0.03, f'{y:.2f}', ha='center', fontsize=9, color='#2ca02c')

plt.tight_layout()
plt.subplots_adjust(hspace=0.05) # 调整子图间距
plt.show()