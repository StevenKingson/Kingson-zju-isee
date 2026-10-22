# 第三部分：验证饱和电流与光强的正比关系
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("Part 3: Verify Proportional Relationship between Saturation Current and Light Intensity")
print("Experimental Condition: 436nm monochromatic light, 4mm aperture, Voltage=30.49V")
print("=" * 60)

# 实验数据
distances = np.array([30, 32, 34, 36, 38, 40])  # 光源距离，cm
currents = np.array([175, 143, 126, 108, 88, 83])  # 饱和电流，×10^-10 A

print("Light source distance L (cm):", distances)
print("Saturation current I_s (10^-10 A):", currents)

# 计算相对光强（与1/L²成正比）
intensities = 1 / (distances ** 2)  # 相对光强，1/cm²

print("\nCalculate relative light intensity (1/L^2):")
for i in range(len(distances)):
    print(f"  L={distances[i]}cm, 1/L^2={intensities[i]:.6f} cm^-2, I_s={currents[i]}x10^-10A")

# 线性回归分析
slope, intercept, r_value, p_value, std_err = linregress(intensities, currents)

print(f"\nLinear regression analysis results:")
print(f"  Slope (proportional coefficient): {slope:.2f} (10^-10 A·cm^2)")
print(f"  Intercept: {intercept:.2f} x10^-10 A")
print(f"  Correlation coefficient r: {r_value:.4f}")
print(f"  Coefficient of determination R^2: {r_value**2:.4f}")
print(f"  Standard error: {std_err:.2f}")

# 创建图形（只显示一个主图）
plt.figure(figsize=(10, 8))

# 绘制实验数据点
plt.scatter(intensities, currents, color='red', s=100, zorder=5, label='实验数据')

# 绘制拟合直线
x_fit = np.linspace(intensities.min()*0.9, intensities.max()*1.1, 100)
y_fit = slope * x_fit + intercept
plt.plot(x_fit, y_fit, 'b-', linewidth=3, 
         label=f'线性拟合: y={slope:.1f}x+{intercept:.1f}')

# 计算预测值和残差
y_pred = slope * intensities + intercept

# 绘制残差连线
for i in range(len(intensities)):
    plt.plot([intensities[i], intensities[i]], [currents[i], y_pred[i]], 
             'g--', alpha=0.5, linewidth=1.5)

plt.xlabel('相对光强 1/L^2 (cm^-2)', fontsize=14)
plt.ylabel('饱和电流 I_s (×10^-10 A)', fontsize=14)
plt.title('饱和电流与相对光强关系\n(验证正比关系)', fontsize=16, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(loc='upper left', fontsize=12)

# 在图上标注回归统计信息（调整位置避免重叠）
textstr = f'回归分析结果:\n'
textstr += f'斜率: {slope:.1f} (10^-10 A·cm^2)\n'
textstr += f'截距: {intercept:.1f} ×10^-10 A\n'
textstr += f'相关系数 r: {r_value:.4f}\n'
textstr += f'决定系数 R^2: {r_value**2:.4f}\n'
textstr += f'方程: I_s = {slope:.1f}·(1/L^2) + {intercept:.1f}'

props = dict(boxstyle='round', facecolor='lightblue', alpha=0.9)
plt.text(0.05, 0.90, textstr, transform=plt.gca().transAxes, fontsize=12,
         verticalalignment='top', bbox=props)  # 将y位置从0.95改为0.90

# 在图上标注数据点（光源距离），调整位置避免重叠
for i, (intensity, curr) in enumerate(zip(intensities, currents)):
    # 根据数据点位置调整标注位置
    if i == 0 or i == 5:  # 第一个和最后一个点标注在上方
        va = 'bottom'
        offset = 4
    else:  # 其他点标注在下方
        va = 'top'
        offset = -4
        
    plt.text(intensity, curr+offset, f'L={distances[i]}cm', fontsize=10, 
             ha='center', va=va,
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.show()

# ============================================================================
# 简单的分析输出
# ============================================================================

print("\n" + "=" * 60)
print("Proportional Relationship Verification")
print("=" * 60)

# 计算理论正比关系的比例系数（假设截距为0）
slope_no_intercept = np.sum(currents * intensities) / np.sum(intensities**2)
print(f"1. Proportional coefficient (assuming zero intercept):")
print(f"   k = {slope_no_intercept:.1f} (10^-10 A·cm^2)")

# 计算相对误差
relative_errors = abs((currents - y_pred) / currents) * 100
avg_error = np.mean(relative_errors)

print(f"\n2. Relative errors for each data point:")
for i in range(len(distances)):
    print(f"   L={distances[i]}cm: Measured={currents[i]}, "
          f"Predicted={y_pred[i]:.1f}, Error={relative_errors[i]:.1f}%")

print(f"\n3. Average relative error: {avg_error:.1f}%")

print(f"\n4. Physical interpretation:")
print(f"   The high correlation (r={r_value:.4f}) confirms that")
print(f"   saturation current is approximately proportional to 1/L^2.")
print(f"   This supports the inverse square law for light intensity.")