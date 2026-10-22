import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 实验数据录入 ---
# Rx (Ω), 注意：'2k'转换为2000, 'inf'在绘图中通常截断或单独处理
Rx_data = np.array([0, 100, 200, 500, 1000, 1500, 2000, 3000, 5000, 10000, 30000])
# 对应的电流 I (mA)
I_data = np.array([1.00, 0.74, 0.60, 0.36, 0.22, 0.15, 0.11, 0.07, 0.04, 0.01, 0.00])

# --- 理论计算参数 ---
# 根据题意：I_max = 1mA (Rx=0时), 中值电阻 R_center (即欧姆表内阻) ≈ 300Ω
# 理论公式: I = I_max * (R_int / (R_int + Rx))
R_int = 300  # 欧姆表内阻
I_max = 1.0  # 满偏电流

# 生成平滑的理论曲线数据 (从0到10000，太大的值会导致图形压缩看不清)
Rx_theory = np.linspace(0, 5000, 500) 
I_theory = I_max * (R_int / (R_int + Rx_theory))

# --- 绘图 ---
plt.figure(figsize=(9, 6), dpi=100)

# 1. 绘制理论曲线
plt.plot(Rx_theory, I_theory, color='blue', linestyle='-', linewidth=2, label='理论特性曲线 ($R_{内}=300\Omega$)')

# 2. 绘制实验数据点 (只画到5000欧姆以便观察，大电阻点在图外或边缘)
# 为了图表清晰，我们截取Rx <= 5000的数据点进行展示
mask = Rx_data <= 5000
plt.scatter(Rx_data[mask], I_data[mask], color='red', s=60, zorder=5, label='实验测量点')

# 设置坐标轴
plt.xlim(0, 5200)
plt.ylim(0, 1.1)
plt.title('欧姆表改装实验：表头电流 $I$ 与待测电阻 $R_x$ 关系曲线', fontsize=14)
plt.xlabel('待测电阻 $R_x$ / $\Omega$', fontsize=12)
plt.ylabel('表头电流 $I$ / mA', fontsize=12)

# 网格与图例
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

# 标注关键点 (中值电阻)
plt.annotate(f'中值电阻\n$R_x=300\Omega, I=0.5mA$', xy=(300, 0.5), xytext=(1000, 0.6),
             arrowprops=dict(facecolor='black', shrink=0.05))

# 标注数据点数值
for x, y in zip(Rx_data[mask], I_data[mask]):
    plt.text(x, y + 0.02, f'{y:.2f}', ha='center', fontsize=9)

plt.show()