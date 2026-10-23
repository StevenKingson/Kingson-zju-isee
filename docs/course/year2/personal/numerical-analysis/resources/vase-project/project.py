import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, lagrange

y_points = np.array([-7.0, -6.5, -5.5, -4.0, -2.0,  0.0,  2.0, 4.0, 5.5, 6.2, 6.5, 6.8, 7.0])
x_points = np.array([ 2.5,  1.8,  2.0,  3.5,  4.4,  4.5,  3.5, 2.2, 1.5, 1.8, 2.2, 2.1, 2.0])

# == 方法一：三次样条插值 ==
y_continuous_spline = np.linspace(y_points.min(), y_points.max(), 500)
cs = CubicSpline(y_points, x_points)
x_spline = cs(y_continuous_spline)


# == 方法二：精细化分段拉格朗日插值 ==
# 将轮廓分解为6个二次多项式分段
segments_y = []
segments_x = []

# 定义每个分段的起始点索引 (共13个点，索引为0-12)
# 分段为 [0,1,2], [2,3,4], [4,5,6], [6,7,8], [8,9,10], [10,11,12]
segment_indices = [0, 2, 4, 6, 8, 10]

for i in segment_indices:
    # 每个分段取3个点 (例如 i=0, 取 0,1,2)
    y_seg = y_points[i:i+3]
    x_seg = x_points[i:i+3]
    
    # 创建二次拉格朗日多项式
    poly_seg = lagrange(y_seg, x_seg)
    
    # 在该分段的y区间内生成绘图点
    y_plot_seg = np.linspace(y_seg[0], y_seg[2], 50)
    x_plot_seg = poly_seg(y_plot_seg)
    
    segments_y.append(y_plot_seg)
    segments_x.append(x_plot_seg)

# 合并所有分段的结果
y_piecewise_revised = np.concatenate(segments_y)
x_piecewise_revised = np.concatenate(segments_x)


# --- 3. 结果可视化 ---

def plot_vase(y_coords, x_coords, title, original_y, original_x):
    """
    绘制完整、封闭的花瓶轮廓
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(7, 9))

    # 绘制右侧和左侧轮廓
    ax.plot(x_coords, y_coords, color='darkorange', label='Right Contour (Fitted)')
    ax.plot(-x_coords, y_coords, color='green', label='Left Contour (Mirrored)')

    # 绘制顶部和底部的封口线
    x_bottom = x_coords[0]
    x_top = x_coords[-1]
    ax.plot([-x_bottom, x_bottom], [y_coords.min(), y_coords.min()], color='gray', linestyle='--')
    ax.plot([-x_top, x_top], [y_coords.max(), y_coords.max()], color='gray', linestyle='--')

    # 绘制原始数据点
    ax.plot(original_x, original_y, 'o', color='royalblue', markersize=6, label=f'Original Data Points ({len(original_x)} points)')
    ax.plot(-original_x, original_y, 'o', color='royalblue', markersize=6)

    # 美化图表
    ax.set_title(title, fontsize=16, pad=15)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.axhline(0, color='black', linewidth=0.75, alpha=0.5)
    ax.axvline(0, color='black', linewidth=0.75, alpha=0.5)
    ax.axis('equal')
    ax.legend()
    ax.grid(True)
    plt.show()

# 调用绘图函数
# 1. 显示三次样条的结果作为对照
plot_vase(y_continuous_spline, x_spline, 'Vase Reconstruction using Cubic Spline', y_points, x_points)

# 2. 显示修正后的分段拉格朗日结果
plot_vase(y_piecewise_revised, x_piecewise_revised, 'Vase Reconstruction using Revised Piecewise Lagrange', y_points, x_points)