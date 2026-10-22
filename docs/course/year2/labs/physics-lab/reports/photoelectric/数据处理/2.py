# 第二部分：伏安特性曲线绘制
import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("第二部分：光电管伏安特性曲线绘制")
print("实验条件：436nm单色光，4mm光阑，40cm光源距离")
print("=" * 60)

# 实验数据
voltage = np.array([0.00, 0.5, 1.00, 1.55, 1.72, 2.33, 3.06, 4.00, 5.06, 
                    5.91, 7.44, 9.00, 11.47, 12.92, 15.56, 17.88, 21.12, 
                    23.84, 25.02, 28.28, 30.49])  # 光电管电压，V

current = np.array([2, 6, 11, 16, 18, 24, 29, 34, 39, 42, 48, 52, 59, 
                    65, 68, 70, 76, 77, 80, 82, 83])  # 电流，×10^-10 A

print(f"实验数据点数: {len(voltage)}")
print(f"电压范围: {voltage.min():.2f} - {voltage.max():.2f} V")
print(f"电流范围: {current.min()} - {current.max()} ×10^-10 A")

# 绘制伏安特性曲线
plt.figure(figsize=(10, 7))

# 绘制完整的伏安特性曲线
plt.plot(voltage, current, 'b-o', linewidth=2, markersize=7, 
         label='436nm单色光伏安特性曲线')

# 用不同颜色标记三个区域
# 1. 快速上升区 (0-5V)
rise_mask = voltage <= 5
plt.plot(voltage[rise_mask], current[rise_mask], 'ro', 
         markersize=7, label='快速上升区 (0-5V)', zorder=5)

# 2. 过渡区 (5-15V)
trans_mask = (voltage > 5) & (voltage <= 15)
plt.plot(voltage[trans_mask], current[trans_mask], 'go', 
         markersize=6, label='过渡区 (5-15V)', zorder=4)

# 3. 较高电压区 (>15V)
high_mask = voltage > 15
plt.plot(voltage[high_mask], current[high_mask], 'mo', 
         markersize=6, label='较高电压区 (>15V)', zorder=3)

# 设置图表属性
plt.xlabel('光电管电压 $U_{AK}$ (V)', fontsize=12)
plt.ylabel('光电流 $I$ (×10$^{-10}$ A)', fontsize=12)
plt.title('436nm单色光照射下的光电管伏安特性曲线', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(loc='lower right', fontsize=10)

# 设置坐标轴范围，留出一些空间
plt.xlim(-1, 32)
plt.ylim(-2, 90)

# 添加网格线
plt.grid(True, alpha=0.3, linestyle='--')

# 添加分界线
plt.axvline(x=5, color='r', linestyle=':', alpha=0.5, linewidth=1)
plt.axvline(x=15, color='b', linestyle=':', alpha=0.5, linewidth=1)

# 在图中添加一些关键数据点的标注
for i in [0, 5, 10, 15, 20]:
    if i < len(voltage):
        plt.text(voltage[i], current[i]+1.5, f'({voltage[i]}, {current[i]})', 
                fontsize=9, ha='center', bbox=dict(boxstyle='round,pad=0.3', 
                facecolor='white', alpha=0.7))

# 添加区域说明
plt.text(2.5, 60, '快速上升区\n电压较低时电流\n随电压快速增加', 
         fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='red', alpha=0.1))
plt.text(10, 45, '过渡区\n电流增长\n逐渐减缓', 
         fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='green', alpha=0.1))
plt.text(23, 30, '较高电压区\n电流变化趋缓', 
         fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='purple', alpha=0.1))

plt.tight_layout()
plt.show()

# ============================================================================
# 数据分析
# ============================================================================

print("\n" + "=" * 60)
print("伏安特性曲线分析")
print("=" * 60)

# 1. 计算不同区域的电流变化特征
print("1. 不同电压区域的电流变化特征:")

# 快速上升区 (0-5V)
if np.sum(rise_mask) > 1:
    rise_voltages = voltage[rise_mask]
    rise_currents = current[rise_mask]
    rise_ratio = (rise_currents[-1] - rise_currents[0]) / (rise_voltages[-1] - rise_voltages[0])
    print(f"   快速上升区 (0-5V):")
    print(f"   电压范围: {rise_voltages[0]:.2f} - {rise_voltages[-1]:.2f} V")
    print(f"   电流范围: {rise_currents[0]} - {rise_currents[-1]} ×10^-10 A")
    print(f"   平均变化率: {rise_ratio:.2f} (10^-10 A/V)")
    print(f"   电流增加了 {rise_currents[-1] - rise_currents[0]} ×10^-10 A")

# 过渡区 (5-15V)
if np.sum(trans_mask) > 1:
    trans_voltages = voltage[trans_mask]
    trans_currents = current[trans_mask]
    trans_ratio = (trans_currents[-1] - trans_currents[0]) / (trans_voltages[-1] - trans_voltages[0])
    print(f"\n   过渡区 (5-15V):")
    print(f"   电压范围: {trans_voltages[0]:.2f} - {trans_voltages[-1]:.2f} V")
    print(f"   电流范围: {trans_currents[0]} - {trans_currents[-1]} ×10^-10 A")
    print(f"   平均变化率: {trans_ratio:.2f} (10^-10 A/V)")
    print(f"   电流增加了 {trans_currents[-1] - trans_currents[0]} ×10^-10 A")

# 较高电压区 (>15V)
if np.sum(high_mask) > 1:
    high_voltages = voltage[high_mask]
    high_currents = current[high_mask]
    high_ratio = (high_currents[-1] - high_currents[0]) / (high_voltages[-1] - high_voltages[0])
    print(f"\n   较高电压区 (>15V):")
    print(f"   电压范围: {high_voltages[0]:.2f} - {high_voltages[-1]:.2f} V")
    print(f"   电流范围: {high_currents[0]} - {high_currents[-1]} ×10^-10 A")
    print(f"   平均变化率: {high_ratio:.2f} (10^-10 A/V)")
    print(f"   电流增加了 {high_currents[-1] - high_currents[0]} ×10^-10 A")

# 2. 计算总体电流变化
print(f"\n2. 总体电流变化:")
print(f"   电压从 {voltage[0]:.2f} V 增加到 {voltage[-1]:.2f} V")
print(f"   电流从 {current[0]} 增加到 {current[-1]} ×10^-10 A")
print(f"   总电流增加: {current[-1] - current[0]} ×10^-10 A")
print(f"   总体平均变化率: {(current[-1] - current[0])/(voltage[-1] - voltage[0]):.2f} (10^-10 A/V)")

# 3. 光电管特性描述
print(f"\n3. 光电管特性描述:")
print(f"   a) 在低电压区域(0-5V)，光电流随电压快速增加")
print(f"   b) 在中等电压区域(5-15V)，光电流增加速度逐渐减缓")
print(f"   c) 在较高电压区域(>15V)，光电流增加非常缓慢")
print(f"   d) 曲线形状符合光电管的基本伏安特性")

print("\n" + "=" * 60)
print("实验结论:")
print("=" * 60)
print("1. 光电管的伏安特性曲线显示了光电流随电压变化的典型特征")
print("2. 在低电压时，电压对光电子收集效率影响显著")
print("3. 随着电压增加，电流增长逐渐趋缓")
print("4. 实验数据验证了光电管的基本工作原理")