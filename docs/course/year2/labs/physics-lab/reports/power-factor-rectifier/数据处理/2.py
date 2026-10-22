import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

# 数据定义
C = np.array([0, 1, 2, 3, 4, 5, 6, 7])  # 电容C/μF
I = np.array([307.8, 237.7, 181.4, 146.1, 121.9, 132.5, 160.2, 173.7])  # 电流I/mA
U = np.array([226.1, 226.3, 226.1, 226.1, 226.4, 226.7, 226.6, 226.4])  # 电压U/V
P = np.array([24.1, 24.7, 24.8, 24.9, 25.0, 25.2, 25.1, 25.3])  # 功率P/W

# 生成平滑曲线用的新x值
C_new = np.linspace(0, 7, 300)

# 创建图形和子图
fig = plt.figure(figsize=(15, 5))

# 第一张图：电容与电流的关系
ax1 = fig.add_subplot(131)
model_I = make_interp_spline(C, I)
I_new = model_I(C_new)
ax1.scatter(C, I, color='red', zorder=5)
ax1.plot(C_new, I_new, color='red', linewidth=2)
ax1.set_title('并联电容与电流的关系')
ax1.set_xlabel('并联电容C/μF')
ax1.set_ylabel('电流I/mA', rotation=0, y=1.02, labelpad=0)
ax1.grid(linestyle=':', alpha=0.6)
ax1.set_xlim(-0.5, 7.5)

# 第二张图：电容与电压的关系
ax2 = fig.add_subplot(132)
model_U = make_interp_spline(C, U)
U_new = model_U(C_new)
ax2.scatter(C, U, color='blue', zorder=5)
ax2.plot(C_new, U_new, color='blue', linewidth=2)
ax2.set_title('并联电容与电压的关系')
ax2.set_xlabel('并联电容C/μF')
ax2.set_ylabel('电压U/V', rotation=0, y=1.02, labelpad=0)
ax2.grid(linestyle=':', alpha=0.6)
ax2.set_xlim(-0.5, 7.5)
# 调整电压图的分度，使曲线看起来更平
ax2.set_ylim(200, 250)  # 设置y轴范围为225V到228V
ax2.set_yticks(np.arange(200, 250, 10))  # 设置刻度为每0.5V一个

# 第三张图：电容与功率的关系
ax3 = fig.add_subplot(133)
model_P = make_interp_spline(C, P)
P_new = model_P(C_new)
ax3.scatter(C, P, color='green', zorder=5)
ax3.plot(C_new, P_new, color='green', linewidth=2)
ax3.set_title('并联电容与功率的关系')
ax3.set_xlabel('并联电容C/μF')
ax3.set_ylabel('功率P/W', rotation=0, y=1.02, labelpad=0)
ax3.grid(linestyle=':', alpha=0.6)
ax3.set_xlim(-0.5, 7.5)
# 调整功率图的分度，使曲线看起来更平
ax3.set_ylim(20, 30)  # 设置y轴范围为23.5W到26W
ax3.set_yticks(np.arange(20, 30, 1))  # 设置刻度为每0.5W一个

# 调整子图间距
plt.tight_layout()

# 显示图形
plt.show()