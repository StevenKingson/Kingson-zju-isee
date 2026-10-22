# 第四部分：验证饱和电流与光强的正比关系（光阑孔径实验）
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("Part 4: Verify Proportional Relationship between Saturation Current and Light Intensity (Aperture)")
print("Experimental Condition: 436nm monochromatic light, 40cm distance, Voltage=30.49V")
print("=" * 60)

# 实验数据
apertures = np.array([2, 4, 8])  # 光阑孔径，mm
currents = np.array([19, 83, 322])  # 饱和电流，×10^-10 A

print("Aperture diameter Φ (mm):", apertures)
print("Saturation current I_s (10^-10 A):", currents)

# 计算光阑面积（与光强成正比）
areas = np.pi * (apertures / 2) ** 2  # 光阑面积，mm²

print("\nCalculate aperture area (π·(Φ/2)^2):")
for i in range(len(apertures)):
    print(f"  Φ={apertures[i]}mm, Area={areas[i]:.2f} mm^2, I_s={currents[i]}x10^-10A")

# 线性回归分析
slope, intercept, r_value, p_value, std_err = linregress(areas, currents)

print(f"\nLinear regression analysis results:")
print(f"  Slope (proportional coefficient): {slope:.2f} (10^-10 A/mm^2)")
print(f"  Intercept: {intercept:.2f} x10^-10 A")
print(f"  Correlation coefficient r: {r_value:.4f}")
print(f"  Coefficient of determination R^2: {r_value**2:.4f}")
print(f"  Standard error: {std_err:.2f}")

# 创建图形
plt.figure(figsize=(10, 8))

# 绘制实验数据点
plt.scatter(areas, currents, color='red', s=150, zorder=5, label='实验数据')

# 绘制拟合直线
x_fit = np.linspace(0, areas.max()*1.1, 100)
y_fit = slope * x_fit + intercept
plt.plot(x_fit, y_fit, 'b-', linewidth=3, 
         label=f'线性拟合: y={slope:.1f}x+{intercept:.1f}')

plt.xlabel('光阑面积 (mm^2)', fontsize=14)
plt.ylabel('饱和电流 I_s (×10^-10 A)', fontsize=14)
plt.title('饱和电流与光阑面积关系\n(验证饱和电流与光强正比关系)', fontsize=16, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(loc='upper left', fontsize=12)

# 在图上标注回归统计信息
textstr = f'回归分析结果:\n'
textstr += f'斜率: {slope:.1f} (10^-10 A/mm^2)\n'
textstr += f'截距: {intercept:.1f} ×10^-10 A\n'
textstr += f'相关系数 r: {r_value:.4f}\n'
textstr += f'决定系数 R^2: {r_value**2:.4f}\n'
textstr += f'方程: I_s = {slope:.1f}·面积 + {intercept:.1f}'

props = dict(boxstyle='round', facecolor='lightblue', alpha=0.9)
plt.text(0.05, 0.85, textstr, transform=plt.gca().transAxes, fontsize=12,
         verticalalignment='top', bbox=props)

# 在图上标注数据点（光阑孔径）
for i, (area, curr) in enumerate(zip(areas, currents)):
    plt.text(area, curr+10, f'Φ={apertures[i]}mm', fontsize=12, ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# 添加坐标原点参考（理论应过原点）
plt.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle=':', alpha=0.5)

# 设置坐标轴范围
plt.xlim(-5, areas.max()*1.1)
plt.ylim(-20, currents.max()*1.1)

plt.tight_layout()
plt.show()

# ============================================================================
# 额外的验证：电流与孔径直径平方的关系
# ============================================================================

# 计算孔径的平方（与面积成正比）
diameter_squared = apertures ** 2

print("\n" + "=" * 60)
print("Additional Analysis: Current vs. Diameter Squared")
print("=" * 60)

# 对电流与直径平方进行线性回归
slope2, intercept2, r_value2, p_value2, std_err2 = linregress(diameter_squared, currents)

print(f"Linear regression (I_s vs. Φ^2):")
print(f"  Slope: {slope2:.2f} (10^-10 A/mm^2)")
print(f"  Intercept: {intercept2:.2f} x10^-10 A")
print(f"  Correlation coefficient r: {r_value2:.4f}")
print(f"  Coefficient of determination R^2: {r_value2**2:.4f}")

# ============================================================================
# 简单的分析输出
# ============================================================================

print("\n" + "=" * 60)
print("Proportional Relationship Verification")
print("=" * 60)

# 计算理论正比关系的比例系数（假设截距为0）
# 对于过原点的正比关系：I_s = k * 面积
k_area = np.sum(currents * areas) / np.sum(areas**2)
print(f"1. Proportional coefficient (assuming zero intercept, I_s vs. area):")
print(f"   k = {k_area:.2f} (10^-10 A/mm^2)")

# 计算电流与直径平方的比例系数
k_diameter2 = np.sum(currents * diameter_squared) / np.sum(diameter_squared**2)
print(f"2. Proportional coefficient (assuming zero intercept, I_s vs. Φ^2):")
print(f"   k = {k_diameter2:.2f} (10^-10 A/mm^2)")

# 计算相对误差
y_pred = slope * areas + intercept
relative_errors = abs((currents - y_pred) / currents) * 100
avg_error = np.mean(relative_errors)

print(f"\n3. Relative errors for each data point:")
for i in range(len(apertures)):
    print(f"   Φ={apertures[i]}mm: Measured={currents[i]}, "
          f"Predicted={y_pred[i]:.1f}, Error={relative_errors[i]:.1f}%")

print(f"\n4. Average relative error: {avg_error:.1f}%")

# 理论验证：检查电流比是否接近面积比
area_ratio = areas / areas[0]
current_ratio = currents / currents[0]

print(f"\n5. Theoretical verification (relative to Φ=2mm):")
print(f"   Area ratio (relative to Φ=2mm): {area_ratio}")
print(f"   Current ratio (relative to Φ=2mm): {current_ratio}")

for i in range(1, len(apertures)):
    ratio_diff = abs(area_ratio[i] - current_ratio[i]) / area_ratio[i] * 100
    print(f"   For Φ={apertures[i]}mm: Area ratio={area_ratio[i]:.2f}, "
          f"Current ratio={current_ratio[i]:.2f}, Difference={ratio_diff:.1f}%")

print(f"\n6. Physical interpretation:")
print(f"   The high correlation (r={r_value:.4f}) indicates that")
print(f"   saturation current is approximately proportional to aperture area.")
print(f"   Since light intensity is proportional to aperture area at fixed distance,")
print(f"   this confirms that saturation current is proportional to light intensity.")