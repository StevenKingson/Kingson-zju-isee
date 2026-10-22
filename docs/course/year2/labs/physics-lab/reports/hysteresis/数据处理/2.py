import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 表2数据 - 磁滞回线
No = list(range(1, 49))
H_hysteresis = [326.31, 199.38, 99.88, 46.52, 1.822, -27.02, -48.65, -68.82, -81.83, -93.37, 
                -104.91, -112.11, -119.31, -125.08, -127.98, -133.75, -138.05, -140.95, 
                -146.72, -152.49, -162.60, -174.14, -201.51, -241.89, -316.89, -185.68, 
                -97.66, -41.45, -3.95, 24.90, 47.95, 65.26, 79.66, 91.20, 104.58, 108.51, 
                115.75, 122.95, 127.29, 130.15, 135.92, 140.26, 144.60, 151.80, 160.43, 
                176.31, 199.38, 251.31]

B_hysteresis = [383.06, 355.32, 322.58, 292.26, 256.94, 226.77, 196.45, 161.29, 131.05, 95.76, 
                65.52, 32.76, 0.00, -32.76, -63.00, -98.27, -131.05, -161.29, -191.45, -226.77, 
                -256.94, -287.26, -322.58, -352.74, -377.90, -352.74, -320.00, -289.68, -256.94, 
                -221.77, -191.45, -161.29, -128.52, -98.27, -63.00, -32.76, 0.00, 35.27, 65.52, 
                98.27, 128.52, 161.29, 194.03, 226.77, 256.94, 292.26, 322.58, 355.32]

# 创建闭合曲线（添加第1个点到末尾，确保曲线闭合）
H_closed = H_hysteresis + [H_hysteresis[0]]
B_closed = B_hysteresis + [B_hysteresis[0]]

# 方法1：使用格林公式计算闭合曲线面积
area_green = 0
for i in range(len(H_closed)-1):
    area_green += (H_closed[i] * B_closed[i+1] - H_closed[i+1] * B_closed[i])
area_green = abs(area_green) / 2  # 取绝对值并除以2

# 方法2：使用梯形法计算面积
area_trapz = np.trapz(B_closed, H_closed)

# 创建图形
plt.figure(figsize=(12, 8))

# 绘制磁滞回线 - 先绘制闭合曲线
plt.plot(H_closed, B_closed, 'b-', linewidth=2, label='磁滞回线')

# 标记原始数据点（不包括额外添加的闭合点）
plt.scatter(H_hysteresis, B_hysteresis, color='red', s=30, zorder=5)

# 标记每个数据点
for i, (h, b) in enumerate(zip(H_hysteresis, B_hysteresis)):
    plt.annotate(f'{i+1}', (h, b), textcoords="offset points", 
                xytext=(5,5), ha='center', fontsize=8, color='darkred')

# 特别标记第48个点和第1个点，显示它们连接
plt.plot([H_hysteresis[-1], H_hysteresis[0]], [B_hysteresis[-1], B_hysteresis[0]], 
         'b-', linewidth=2, alpha=0.7)

# 标记与坐标轴的交点
# B=0的点（与H轴交点）
zero_B_points = [(H_hysteresis[i], B_hysteresis[i]) for i in range(len(B_hysteresis)) 
                if abs(B_hysteresis[i]) < 1]
# H=0的点（与B轴交点）
zero_H_points = [(H_hysteresis[i], B_hysteresis[i]) for i in range(len(H_hysteresis)) 
                if abs(H_hysteresis[i]) < 5]

# 标记交点
for h, b in zero_B_points:
    plt.plot(h, b, 'go', markersize=8, markeredgecolor='black')
    plt.annotate(f'B=0\nH={h:.1f}', (h, b), textcoords="offset points", 
                xytext=(10,10), ha='left', fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

for h, b in zero_H_points:
    plt.plot(h, b, 'ro', markersize=8, markeredgecolor='black')
    plt.annotate(f'H=0\nB={b:.1f}', (h, b), textcoords="offset points", 
                xytext=(10,-15), ha='left', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))

# 添加坐标轴
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)

# 设置标签和标题
plt.xlabel('$H$ (A/m)', fontsize=14, style='italic')
plt.ylabel('$B$ (mT)', fontsize=14, style='italic')
plt.title('磁滞回线图', fontsize=16, fontweight='bold')

# 添加网格和图例
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)

# 在图中显示面积计算结果
plt.text(0.05, 0.95, f'磁滞损耗 (闭合曲线面积) = {area_green/1000:.1f} J/m^3', 
         transform=plt.gca().transAxes, fontsize=11,
         bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8),
         verticalalignment='top')

plt.tight_layout()
plt.show()

# 打印详细结果
print("磁滞回线分析结果:")
print(f"格林公式计算面积: {area_green:.2f} J/m³")
print(f"梯形法计算面积: {abs(area_trapz):.2f} J/m³")
print(f"与B轴交点 (H=0时): {zero_H_points}")
print(f"与H轴交点 (B=0时): {zero_B_points}")

# 计算剩磁和矫顽力
if zero_H_points:
    Br = zero_H_points[0][1]  # 第一个H=0点的B值
    print(f"剩磁 B_r = {Br:.2f} mT")

if zero_B_points:
    Hc = abs(zero_B_points[0][0])  # 第一个B=0点的H值的绝对值
    print(f"矫顽力 H_c = {Hc:.2f} A/m")