import matplotlib.pyplot as plt
import numpy as np

# 实验数据
t = np.array([14.9, 22.1, 26.9, 32.3, 36.9, 41.5, 46.2, 51.0])
R = np.array([53.93, 55.46, 56.49, 57.66, 58.63, 59.63, 60.66, 61.66])

# 线性拟合
coefficients = np.polyfit(t, R, 1)
k = coefficients[0]
b = coefficients[1]
fit_line = k * t + b

# 绘图
plt.figure(figsize=(8, 6))
plt.scatter(t, R, color='blue', label='Experimental Data', zorder=5)
plt.plot(t, fit_line, color='red', linestyle='--', label=f'Linear Fit: Rt={k:.4f}t + {b:.2f}')
plt.title('Resistance-Temperature Characteristic Curve of Cu50')
plt.xlabel('Temperature t (℃)')
plt.ylabel('Resistance Rt (Ω)')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.show()

print(f"斜率 k: {k}")
print(f"截距 b: {b}")