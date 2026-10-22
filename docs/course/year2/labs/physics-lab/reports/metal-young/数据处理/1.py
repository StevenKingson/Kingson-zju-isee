import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 实验数据
m = np.array([1, 2, 3, 4, 5, 6, 7, 8])  # 质量 (kg)
s_avg = np.array([24.55, 31.20, 36.90, 44.35, 51.40, 58.25, 65.10, 72.25])  # 标尺读数平均值 (mm)

# 线性回归
slope, intercept, r_value, p_value, std_err = stats.linregress(m, s_avg)

# 计算拟合值
s_fit = slope * m + intercept

# 计算残差
residuals = s_avg - s_fit

# 创建图表
plt.figure(figsize=(12, 5))

# 子图1：拟合直线和原始数据
plt.subplot(1, 2, 1)
plt.scatter(m, s_avg, color='red', label='实验数据', zorder=5)
plt.plot(m, s_fit, 'b-', label=f'拟合直线: s = {slope:.4f}m + {intercept:.4f}')
plt.xlabel('质量 m (kg)')
plt.ylabel('标尺读数 s (mm)')
plt.title('标尺读数与质量的关系')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# 在图上添加拟合方程和R²值
equation_text = f's = {slope:.4f}m + {intercept:.4f}\nR^2 = {r_value**2:.6f}'
plt.text(0.05, 0.95, equation_text, transform=plt.gca().transAxes, 
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 子图2：残差图
plt.subplot(1, 2, 2)
plt.scatter(m, residuals, color='green', label='残差', zorder=5)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('质量 m (kg)')
plt.ylabel('残差 (mm)')
plt.title('残差分析')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

plt.tight_layout()
plt.show()

# 输出拟合结果
print("=" * 50)
print("线性拟合结果")
print("=" * 50)
print(f"斜率 k = {slope:.6f} mm/kg")
print(f"截距 b = {intercept:.6f} mm")
print(f"相关系数 R = {r_value:.6f}")
print(f"决定系数 R^2 = {r_value**2:.6f}")
print(f"标准误差 = {std_err:.6f}")
print(f"拟合方程: s = {slope:.4f}m + {intercept:.4f}")

# 计算每个Δs_i
print("\n" + "=" * 50)
print("Δs_i 计算")
print("=" * 50)
for i in range(4):
    delta_s = (s_avg[i+4] - s_avg[i]) / 4
    print(f"Δs_{i+1} = ({s_avg[i+4]} - {s_avg[i]})/4 = {delta_s:.4f} mm")

# 计算平均Δs
delta_s_values = [(s_avg[i+4] - s_avg[i]) / 4 for i in range(4)]
avg_delta_s = np.mean(delta_s_values)
print(f"\n平均 Δs = {avg_delta_s:.4f} mm")

# 计算Δs的A类不确定度
delta_A_delta_s = np.std(delta_s_values, ddof=1) / np.sqrt(4)
print(f"Δs的A类不确定度 = {delta_A_delta_s:.4f} mm")