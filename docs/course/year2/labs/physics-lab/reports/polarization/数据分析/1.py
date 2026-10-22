import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 实验数据
beta = np.array([75, 85, 95, 105, 115, 125, 135, 145])  # 角坐标β
phi = np.array([-4, -14, -24, -34, -44, -54, -64, -74])  # ϕ=β-Δβ
I_measured = np.array([203, 195.0, 174.5, 145.1, 109.8, 73.6, 40.6, 16.3])  # 光电流(μA)
I_background = 0.3  # 本底光电流(μA)

# 计算净光电流
I_net = I_measured - I_background

# 估计I0 (ϕ=0°时的光电流)
# 通过外推或拟合来估计I0
def malus_law(phi, I0, I1):
    return (I0 - I1) * np.cos(np.radians(phi))**2 + I1

# 使用曲线拟合来估计I0
p0 = [200, I_background]  # 初始猜测值
popt, pcov = curve_fit(malus_law, phi, I_measured, p0=p0)
I0_estimated = popt[0]

print(f"估计的I0值: {I0_estimated:.2f} μA")

# 计算横坐标: (I0 - I1) * cos²ϕ
x_data = (I0_estimated - I_background) * np.cos(np.radians(phi))**2

# 纵坐标: I - I1
y_data = I_net

# 线性拟合
def linear_func(x, a, b):
    return a * x + b

popt_linear, pcov_linear = curve_fit(linear_func, x_data, y_data)
slope = popt_linear[0]
intercept = popt_linear[1]

print(f"拟合直线斜率: {slope:.4f}")
print(f"拟合直线截距: {intercept:.4f}")

# 绘制图形
plt.figure(figsize=(10, 8))

# 散点图
plt.scatter(x_data, y_data, color='blue', s=80, label='实验数据', zorder=5)

# 拟合直线
x_fit = np.linspace(0, max(x_data)*1.1, 100)
y_fit = linear_func(x_fit, *popt_linear)
plt.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'拟合直线: y = {slope:.4f}x + {intercept:.4f}')

# 理论直线 (y = x)
plt.plot(x_fit, x_fit, 'g--', linewidth=2, label='理论直线: y = x', alpha=0.7)

plt.xlabel('$(I_0 - I_1) \\cos^2 \\phi$ (μA)', fontsize=14)
plt.ylabel('$I - I_1$ (μA)', fontsize=14)
plt.title('验证马吕斯定律: $I - I_1$ 与 $(I_0 - I_1)\\cos^2\\phi$ 的关系', fontsize=16)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)
plt.xlim(0, max(x_data)*1.1)
plt.ylim(0, max(y_data)*1.1)

# 添加数据表格
table_data = []
for i in range(len(phi)):
    table_data.append([
        f"{beta[i]}°", 
        f"{phi[i]}°", 
        f"{I_measured[i]}", 
        f"{x_data[i]:.1f}", 
        f"{y_data[i]:.1f}"
    ])

plt.tight_layout()
plt.show()

# 打印详细数据
print("\n详细数据:")
print("β(°)   ϕ(°)   测量电流(μA)  (I₀-I₁)cos²ϕ  I-I₁")
print("-" * 55)
for i in range(len(phi)):
    print(f"{beta[i]:3}   {phi[i]:3}   {I_measured[i]:8.1f}   {x_data[i]:11.1f}   {y_data[i]:8.1f}")

# 计算相关系数
correlation = np.corrcoef(x_data, y_data)[0, 1]
print(f"\n相关系数: {correlation:.6f}")

# 计算相对误差
theoretical_y = x_data
relative_errors = np.abs((y_data - theoretical_y) / theoretical_y) * 100
print(f"\n各数据点相对误差(%):")
for i, error in enumerate(relative_errors):
    print(f"点 {i+1}: {error:.2f}%")

print(f"平均相对误差: {np.mean(relative_errors):.2f}%")