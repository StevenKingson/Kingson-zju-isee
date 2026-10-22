# 第一部分：普朗克常数计算
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 50)
print("Part 1: Planck Constant Calculation")
print("=" * 50)

# 物理常数
e = 1.602e-19  # 元电荷，C
c = 3.0e8      # 光速，m/s
h_accepted = 6.626e-34  # 普朗克常数公认值，J·s

# 实验数据
wavelengths = np.array([365, 405, 436, 546, 577])  # 波长，nm
U_a = np.array([-1.780, -1.414, -1.169, -0.675, -0.536])  # 截止电压，V

# 转换为频率 (ν = c/λ)
frequencies = c / (wavelengths * 1e-9)  # 频率，Hz

print("Wavelengths (nm):", wavelengths)
print("Cut-off Voltage (V):", U_a)
print("Frequencies (10^14 Hz):", [f"{freq/1e14:.3f}" for freq in frequencies])

# 取截止电压的绝对值进行拟合
U_a_abs = np.abs(U_a)

# 线性拟合：e|U_a| = hν - W
def linear_func(nu, h, W):
    return (h * nu - W) / e

# 使用curve_fit进行拟合，提供初始猜测值
initial_guess = [6e-34, 2e-19]
popt, pcov = curve_fit(linear_func, frequencies, U_a_abs, p0=initial_guess)
h_fitted = popt[0]  # 拟合得到的普朗克常数
W_fitted = popt[1]  # 拟合得到的功函数

# 计算标准偏差
perr = np.sqrt(np.diag(pcov))
h_err = perr[0]
W_err = perr[1]

# 计算斜率 (h/e) 和截距 (W/e)
slope = h_fitted / e
intercept = -W_fitted / e

# 计算红限频率
nu_0 = W_fitted / h_fitted
nu_0_err = nu_0 * np.sqrt((h_err/h_fitted)**2 + (W_err/W_fitted)**2)

# 计算相对不确定度
relative_error = abs(h_fitted - h_accepted) / h_accepted * 100

print("\nFitting Results:")
print(f"Planck Constant h = ({h_fitted:.4e} ± {h_err:.4e}) J·s")
print(f"Work Function W = ({W_fitted:.4e} ± {W_err:.4e}) J")
print(f"Slope (h/e) = {slope:.4e} V/Hz")
print(f"Intercept (-W/e) = {intercept:.4f} V")
print(f"Cut-off Frequency v0 = ({nu_0:.3e} ± {nu_0_err:.3e}) Hz")
print(f"Relative Uncertainty: {relative_error:.2f}%")

# 绘制拟合曲线
plt.figure(figsize=(9, 6))
nu_fit = np.linspace(frequencies.min()*0.95, frequencies.max()*1.05, 100)
U_fit = linear_func(nu_fit, h_fitted, W_fitted)

plt.plot(frequencies/1e14, U_a_abs, 'bo', markersize=8, label='实验数据')
plt.plot(nu_fit/1e14, U_fit, 'r-', linewidth=2, label='线性拟合')

# 标注每个数据点的值
for i, (freq, U) in enumerate(zip(frequencies/1e14, U_a_abs)):
    plt.text(freq, U, f'({freq:.2f}, {U:.3f})', fontsize=9, 
             ha='center', va='bottom')

# 在图中标注拟合的直线方程
if intercept >= 0:
    equation = f'拟合方程: y = {slope:.4e}·x + {intercept:.4f}'
else:
    equation = f'拟合方程: y = {slope:.4e}·x - {abs(intercept):.4f}'

plt.text(0.65, 0.25, equation, 
         transform=plt.gca().transAxes, fontsize=12,
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

# 也可以添加光电效应方程作为参考
plt.text(0.65, 0.15, r'光电效应方程: $e|U_a| = h\nu - W$', 
         transform=plt.gca().transAxes, fontsize=12,
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

plt.xlabel('频率 ν (10^14 Hz)')
plt.ylabel('截止电压 |U_a| (V)')
plt.title('光电效应：截止电压与频率关系')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend()

plt.tight_layout()
plt.show()

# 输出详细的计算过程
print("\nDetailed Calculation Process:")
for i, (wl, U, nu) in enumerate(zip(wavelengths, U_a, frequencies)):
    print(f"Filter {i+1}: λ={wl}nm, U_a={U}V, ν={nu/1e14:.2f}×10^14Hz, |U_a|={abs(U):.3f}V")

print(f"\nPhotoelectric Effect Equation: e|U_a| = hν - W")
print(f"Linear Form: |U_a| = (h/e)·ν - (W/e)")
print(f"Fitted: h = {h_fitted:.4e} J·s, W = {W_fitted:.4e} J")
print(f"Cut-off Wavelength: {c/nu_0*1e9:.1f} nm")