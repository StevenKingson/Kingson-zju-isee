import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

x = np.array([0, 1, 2, 3, 4, 5, 6, 7])
y = np.array([0.346, 0.459, 0.605, 0.753, 0.906, 0.842, 0.691, 0.643])
x_new = np.linspace(0, 7, 300)
model = make_interp_spline(x, y)
y_new = model(x_new)

fig = plt.figure()

ax1 = fig.add_subplot(111)
ax1.scatter(x, y)
ax1.plot(x_new, y_new)
ax1.set_title('功率因数与并联电容的关系')
ax1.set_xlabel('并联电容C/μF')
ax1.set_ylabel('功率因数', rotation=0, y=1.02, labelpad=0)
ax1.grid(linestyle=':', alpha=0.6)
ax1.set_xlim(-1, 8)
ax1.set_ylim(0, 1)

plt.show()