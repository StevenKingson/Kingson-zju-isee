import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize as op

plt.rcParams['font.sans-serif'] = ['SimHei']


def my_func(n, a, b, c):
    return a * n ** 2 + b * n + c


x = [5, 10, 15, 20, 25, 30, 40, 45, 50]
f = [750.1, 748.3, 746.9, 746.3, 745.2, 744.4, 744.1, 742.8, 743.2]

a, b, c = op.curve_fit(my_func, x, f)[0]

x_extend = np.arange(5, 50, 0.1)
f_extend = my_func(x_extend, a, b, c)

f_min = min(f_extend)
x_min = x_extend[np.argmin(f_extend)]

fig = plt.figure()

ax1 = fig.add_subplot(111)
ax1.plot(x_extend, f_extend, c='r')
ax1.scatter(x_min, f_min, marker='o', c='b')
ax1.scatter(x, f, s=30, marker='x', c='b')
ax1.set_xlabel('x/mm')
ax1.set_ylabel('f/Hz', rotation=0, y=1.02, labelpad=-30)
ax1.grid(linestyle=':', alpha=0.6)
ax1.set_xlim(5, 50)
ax1.xaxis.set_major_locator(plt.MultipleLocator(5))
ax1.set_ylim(f_min - 1.0, 751.0)
ax1.yaxis.set_major_locator(plt.MultipleLocator(0.5))
ax1.set_title('f - x 图')

ax1.text(float(x_min), f_min - 0.5, f'最低点: ({x_min:.2f}, {f_min:.3f})',
         fontsize=10, verticalalignment='bottom', horizontalalignment='center')

plt.show()