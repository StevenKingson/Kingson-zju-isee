import numpy as np
import matplotlib.pyplot as plt

# 1. 数据录入
# 温度 t (℃)
t_data = np.array([27.3, 33.0, 39.1, 44.2, 49.4, 54.7, 59.7, 64.8, 70.0, 75.2])
# 电阻 R (10^-3 Ω)
R_data = np.array([4.711, 4.807, 4.926, 5.018, 5.109, 5.206, 5.304, 5.400, 5.495, 5.591])

# 2. 线性拟合 (1次多项式拟合 y = kx + b)
# polyfit 返回值 p[0] 是斜率 k，p[1] 是截距 b
coefficients = np.polyfit(t_data, R_data, 1)
k = coefficients[0]
b = coefficients[1]

# 3. 计算拟合曲线上的点
fit_line = k * t_data + b

# 4. 计算电阻温度系数 alpha
alpha = k / b

# 5. 绘图
plt.figure(figsize=(8, 6))
plt.scatter(t_data, R_data, color='blue', label='Experimental Data', marker='o') # 散点
plt.plot(t_data, fit_line, color='red', label=f'Fit: R = {k:.5f}t + {b:.4f}')   # 拟合线

# 图表装饰
plt.title('Resistance vs Temperature (R-t Plot)')
plt.xlabel('Temperature t (℃)')
plt.ylabel('Resistance R (10^-3 Ω)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

# 显示计算结果
print(f"斜率 k = {k:.6f}")
print(f"截距 b = {b:.6f}")
print(f"温度系数 alpha = k/b = {alpha:.6f} (即 {alpha*1000:.4f} x 10^-3)")

plt.show()