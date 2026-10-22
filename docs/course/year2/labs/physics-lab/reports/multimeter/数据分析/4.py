import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def draw_ohmmeter_dial():
    # 参数设置
    R_internal = 300  # 欧姆表内阻 (中值电阻)
    
    # 定义刻度值 (你可以根据需要增减)
    # 这些是我们要显示在表盘上的电阻值
    ticks_values = [0, 50, 100, 200, 300, 500, 1000, 2000, 5000, np.inf]
    
    # 创建画布
    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    
    # 隐藏坐标轴
    ax.set_axis_off()
    ax.set_aspect('equal')
    
    # --- 绘制表盘外框 (扇形) ---
    # 角度范围：从 150度(左) 到 30度(右)，共120度范围
    angle_start = 30
    angle_end = 150
    radius = 10
    
    # 绘制最外层弧线
    arc = patches.Arc((0, 0), radius*2, radius*2, angle=0, 
                      theta1=angle_start, theta2=angle_end, linewidth=2, color='black')
    ax.add_patch(arc)
    
    # 绘制圆心指针轴
    ax.add_patch(plt.Circle((0, 0), 0.5, color='black'))
    
    # --- 计算并绘制刻度 ---
    # 原理：角度与电流成线性关系，但电流与电阻是非线性关系
    # I_ratio = I / I_max = R_internal / (R_internal + Rx)
    # Angle = Angle_0 + (Angle_inf - Angle_0) * (1 - I_ratio)  <-- 注意方向
    # 简单来说：Rx=0 -> I=1 -> 右边(30度); Rx=inf -> I=0 -> 左边(150度)
    
    for r_val in ticks_values:
        # 1. 计算电流比例 (0到1之间)
        if r_val == np.inf:
            current_ratio = 0
            label_text = "∞"
        else:
            current_ratio = R_internal / (R_internal + r_val)
            label_text = str(r_val)
        
        # 2. 映射到角度
        # 0对应30度，1对应150度? 不，1对应30度(右)，0对应150度(左)
        # 角度 = 150 - (150 - 30) * current_ratio
        angle_deg = 150 - (120 * current_ratio)
        angle_rad = np.radians(angle_deg)
        
        # 3. 绘制刻度线
        # 内外半径
        inner_r = radius * 0.90
        outer_r = radius * 1.05
        
        x_start = inner_r * np.cos(angle_rad)
        y_start = inner_r * np.sin(angle_rad)
        x_end = outer_r * np.cos(angle_rad)
        y_end = outer_r * np.sin(angle_rad)
        
        lw = 2 if (r_val == 0 or r_val == np.inf or r_val == 300) else 1
        ax.plot([x_start, x_end], [y_start, y_end], color='black', linewidth=lw)
        
        # 4. 添加文字标签
        text_r = radius * 1.15
        x_text = text_r * np.cos(angle_rad)
        y_text = text_r * np.sin(angle_rad)
        
        # 特殊处理中值电阻的颜色
        color = 'red' if r_val == 300 else 'black'
        font_weight = 'bold' if r_val == 300 else 'normal'
        
        ax.text(x_text, y_text, label_text, ha='center', va='center', 
                fontsize=11, color=color, fontweight=font_weight)

    # --- 添加注释 ---
    ax.text(0, -2, "欧姆表刻度盘示意图 ($R_{mid}=300\Omega$)", ha='center', fontsize=14)
    ax.text(0, 5, "中值电阻\n300Ω", ha='center', fontsize=10, color='red', alpha=0.6)
    
    # 模拟指针 (指向300欧姆位置)
    pointer_angle = np.radians(150 - 120 * 0.5) # 0.5是中值电阻的电流比
    ax.arrow(0, 0, (radius-1)*np.cos(pointer_angle), (radius-1)*np.sin(pointer_angle), 
             head_width=0.3, head_length=0.5, fc='red', ec='red', alpha=0.8)

    # 设置显示范围
    ax.set_xlim(-13, 13)
    ax.set_ylim(-2, 13)
    
    plt.show()

# 运行绘图函数
draw_ohmmeter_dial()