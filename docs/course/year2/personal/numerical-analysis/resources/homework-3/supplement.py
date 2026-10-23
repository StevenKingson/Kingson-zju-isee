import numpy as np
import matplotlib.pyplot as plt

# 设置图形样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class IterativeMethods:
    """迭代方法实现类"""
    
    def __init__(self, A, b, tol=1e-6, max_iter=1000):
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.tol = tol
        self.max_iter = max_iter
        self.n = len(b)
    
    def jacobi_iteration(self, x_old, x_new):
        """雅可比迭代一步"""
        for i in range(self.n):
            sum_ax = 0.0
            for j in range(self.n):
                if j != i:
                    sum_ax += self.A[i, j] * x_old[j]
            x_new[i] = (self.b[i] - sum_ax) / self.A[i, i]
    
    def gauss_seidel_iteration(self, x):
        """高斯-赛德尔迭代一步"""
        for i in range(self.n):
            sum_ax = 0.0
            for j in range(self.n):
                if j != i:
                    sum_ax += self.A[i, j] * x[j]
            x[i] = (self.b[i] - sum_ax) / self.A[i, i]
    
    def solve_jacobi(self, x0=None):
        """雅可比方法求解"""
        if x0 is None:
            x0 = np.zeros(self.n)
        
        x_old = np.array(x0, dtype=float)
        x_new = np.zeros(self.n)
        
        iterations = 0
        errors = []
        solutions = [x_old.copy()]
        
        for k in range(self.max_iter):
            self.jacobi_iteration(x_old, x_new)
            error = np.max(np.abs(x_new - x_old))
            
            errors.append(error)
            solutions.append(x_new.copy())
            iterations += 1
            
            if error < self.tol:
                break
            
            x_old = x_new.copy()
            x_new = np.zeros(self.n)
        
        return x_new, errors, solutions, iterations
    
    def solve_gauss_seidel(self, x0=None):
        """高斯-赛德尔方法求解"""
        if x0 is None:
            x0 = np.zeros(self.n)
        
        x = np.array(x0, dtype=float)
        x_old = x.copy()
        
        iterations = 0
        errors = []
        solutions = [x.copy()]
        
        for k in range(self.max_iter):
            self.gauss_seidel_iteration(x)
            error = np.max(np.abs(x - x_old))
            
            errors.append(error)
            solutions.append(x.copy())
            iterations += 1
            
            if error < self.tol:
                break
            
            x_old = x.copy()
        
        return x, errors, solutions, iterations

def plot_problem1():
    """绘制问题1的图形 - 误差分析"""
    print("生成问题1的图形...")
    
    # 实际解和近似解
    x_actual = np.array([0, -7, 5])
    x_tilde_a = np.array([-0.2, -7.5, 5.4])
    x_tilde_b = np.array([-0.33, -7.9, 5.8])
    
    A = np.array([[1, 2, 3],
                 [2, 3, 4],
                 [3, 4, 6]])
    b = np.array([1, -1, 2])
    
    # 计算误差和残差
    error_a = np.abs(x_actual - x_tilde_a)
    error_b = np.abs(x_actual - x_tilde_b)
    
    residual_a = np.abs(A @ x_tilde_a - b)
    residual_b = np.abs(A @ x_tilde_b - b)
    
    # 绘制误差比较图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 误差比较
    x_labels = ['x1', 'x2', 'x3']
    width = 0.35
    
    ax1.bar(np.arange(len(x_labels)) - width/2, error_a, width, label='近似解a', alpha=0.7, color='skyblue')
    ax1.bar(np.arange(len(x_labels)) + width/2, error_b, width, label='近似解b', alpha=0.7, color='lightcoral')
    
    ax1.set_xlabel('变量')
    ax1.set_ylabel('绝对误差')
    ax1.set_title('问题1 - 近似解与实际解的绝对误差比较')
    ax1.set_xticks(np.arange(len(x_labels)))
    ax1.set_xticklabels(x_labels)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 残差比较
    ax2.bar(np.arange(len(x_labels)) - width/2, residual_a, width, label='近似解a', alpha=0.7, color='skyblue')
    ax2.bar(np.arange(len(x_labels)) + width/2, residual_b, width, label='近似解b', alpha=0.7, color='lightcoral')
    
    ax2.set_xlabel('方程')
    ax2.set_ylabel('残差')
    ax2.set_title('问题1 - 近似解的残差比较')
    ax2.set_xticks(np.arange(len(x_labels)))
    ax2.set_xticklabels(['方程1', '方程2', '方程3'])
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('problem1_errors.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 输出数值结果
    print(f"近似解a:")
    print(f"  ||x - x_tilde||∞ = {np.max(error_a):.6f}")
    print(f"  ||Ax_tilde - b||∞ = {np.max(residual_a):.6f}")
    
    print(f"\n近似解b:")
    print(f"  ||x - x_tilde||∞ = {np.max(error_b):.6f}")
    print(f"  ||Ax_tilde - b||∞ = {np.max(residual_b):.6f}")

def plot_problem3():
    """绘制问题3的图形 - 高斯消元法求解结果"""
    print("生成问题3的图形...")
    
    # 系统a的系数矩阵和右端向量
    A1 = np.array([[0.03, 58.9],
                  [5.31, -6.10]], dtype=float)
    b1 = np.array([59.2, 47.0], dtype=float)
    
    # 系统b的系数矩阵和右端向量
    A2 = np.array([[3.03, -12.1, 14],
                  [-3.03, 12.1, -7],
                  [6.11, -14.2, 21]], dtype=float)
    b2 = np.array([-119, 120, -139], dtype=float)
    
    # 使用numpy求解线性系统
    x1 = np.linalg.solve(A1, b1)
    x2 = np.linalg.solve(A2, b2)
    
    # 绘制结果
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))
    
    # 系统a系数矩阵热图
    im1 = ax1.imshow(A1, cmap='coolwarm', aspect='equal')
    ax1.set_title('系统a - 系数矩阵 A')
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['x1', 'x2'])
    ax1.set_yticks([0, 1])
    ax1.set_yticklabels(['方程1', '方程2'])
    
    # 添加数值标签
    for i in range(2):
        for j in range(2):
            ax1.text(j, i, f'{A1[i, j]:.2f}', ha='center', va='center', 
                    color='white' if abs(A1[i, j]) > 30 else 'black')
    
    plt.colorbar(im1, ax=ax1)
    
    # 系统a解的可视化
    bars1 = ax2.bar(['x1', 'x2'], x1, color=['skyblue', 'lightcoral'], alpha=0.7)
    ax2.set_title('系统a - 解向量')
    ax2.set_ylabel('解的值')
    ax2.grid(True, alpha=0.3)
    
    # 在柱状图上添加数值标签
    for bar, value in zip(bars1, x1):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{value:.2f}', ha='center', va='bottom')
    
    # 系统b系数矩阵热图
    im2 = ax3.imshow(A2, cmap='coolwarm', aspect='equal')
    ax3.set_title('系统b - 系数矩阵 A')
    ax3.set_xticks([0, 1, 2])
    ax3.set_xticklabels(['x1', 'x2', 'x3'])
    ax3.set_yticks([0, 1, 2])
    ax3.set_yticklabels(['方程1', '方程2', '方程3'])
    
    # 添加数值标签
    for i in range(3):
        for j in range(3):
            ax3.text(j, i, f'{A2[i, j]:.2f}', ha='center', va='center', 
                    color='white' if abs(A2[i, j]) > 10 else 'black')
    
    plt.colorbar(im2, ax=ax3)
    
    # 系统b解的可视化
    bars2 = ax4.bar(['x1', 'x2', 'x3'], x2, color=['skyblue', 'lightcoral', 'lightgreen'], alpha=0.7)
    ax4.set_title('系统b - 解向量')
    ax4.set_ylabel('解的值')
    ax4.grid(True, alpha=0.3)
    
    # 在柱状图上添加数值标签
    for bar, value in zip(bars2, x2):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{value:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('problem3_solutions.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 输出数值结果
    print(f"系统a的解: x1 = {x1[0]:.6f}, x2 = {x1[1]:.6f}")
    print(f"系统b的解: x1 = {x2[0]:.6f}, x2 = {x2[1]:.6f}, x3 = {x2[2]:.6f}")

def plot_problem4():
    """绘制问题4的图形 - 雅可比迭代前三次结果"""
    print("生成问题4的图形...")
    
    # 系统a
    A_a = np.array([[4, 1, -1],
                   [-1, 3, 1],
                   [2, 2, 5]], dtype=float)
    b_a = np.array([5, -4, 1], dtype=float)
    
    # 系统b
    A_b = np.array([[-2, 1, 0.5],
                   [1, -2, -0.5],
                   [0, 1, 2]], dtype=float)
    b_b = np.array([4, -4, 0], dtype=float)
    
    # 创建求解器实例
    solver_a = IterativeMethods(A_a, b_a)
    solver_b = IterativeMethods(A_b, b_b)
    
    # 获取前三次迭代结果
    _, _, solutions_a, _ = solver_a.solve_jacobi()
    _, _, solutions_b, _ = solver_b.solve_jacobi()
    
    # 绘制系统a的收敛过程
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    iterations = list(range(min(4, len(solutions_a))))
    x1_a = [sol[0] for sol in solutions_a[:4]]
    x2_a = [sol[1] for sol in solutions_a[:4]]
    x3_a = [sol[2] for sol in solutions_a[:4]]
    
    ax1.plot(iterations, x1_a, 'o-', label='x1', linewidth=2, markersize=8)
    ax1.plot(iterations, x2_a, 's-', label='x2', linewidth=2, markersize=8)
    ax1.plot(iterations, x3_a, '^-', label='x3', linewidth=2, markersize=8)
    
    ax1.set_xlabel('迭代次数')
    ax1.set_ylabel('解的值')
    ax1.set_title('系统a - 雅可比方法前三次迭代')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 绘制系统b的收敛过程
    iterations = list(range(min(4, len(solutions_b))))
    x1_b = [sol[0] for sol in solutions_b[:4]]
    x2_b = [sol[1] for sol in solutions_b[:4]]
    x3_b = [sol[2] for sol in solutions_b[:4]]
    
    ax2.plot(iterations, x1_b, 'o-', label='x1', linewidth=2, markersize=8)
    ax2.plot(iterations, x2_b, 's-', label='x2', linewidth=2, markersize=8)
    ax2.plot(iterations, x3_b, '^-', label='x3', linewidth=2, markersize=8)
    
    ax2.set_xlabel('迭代次数')
    ax2.set_ylabel('解的值')
    ax2.set_title('系统b - 雅可比方法前三次迭代')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('problem4_iterations.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 输出前三次迭代结果
    print("系统a的前三次迭代结果:")
    for i, sol in enumerate(solutions_a[:4]):
        print(f"第{i}次: x1={sol[0]:.6f}, x2={sol[1]:.6f}, x3={sol[2]:.6f}")
    
    print("\n系统b的前三次迭代结果:")
    for i, sol in enumerate(solutions_b[:4]):
        print(f"第{i}次: x1={sol[0]:.6f}, x2={sol[1]:.6f}, x3={sol[2]:.6f}")

def plot_problem5():
    """绘制问题5的图形 - 雅可比和高斯-赛德尔方法比较"""
    print("生成问题5的图形...")
    
    # 系统a
    A5a = np.array([[3, -1, 1],
                   [3, 6, 2],
                   [3, 3, 7]], dtype=float)
    b5a = np.array([1, 0, 4], dtype=float)
    
    # 系统b
    A5b = np.array([[10, -1, 0],
                   [-1, 10, -2],
                   [0, -2, 10]], dtype=float)
    b5b = np.array([9, 7, 6], dtype=float)
    
    # 创建求解器实例
    solver5a = IterativeMethods(A5a, b5a, tol=0.001)
    solver5b = IterativeMethods(A5b, b5b, tol=0.001)
    
    # 求解并获取收敛数据
    x_jacobi_a, errors_jacobi_a, solutions_jacobi_a, iter_jacobi_a = solver5a.solve_jacobi()
    x_gs_a, errors_gs_a, solutions_gs_a, iter_gs_a = solver5a.solve_gauss_seidel()
    
    x_jacobi_b, errors_jacobi_b, solutions_jacobi_b, iter_jacobi_b = solver5b.solve_jacobi()
    x_gs_b, errors_gs_b, solutions_gs_b, iter_gs_b = solver5b.solve_gauss_seidel()
    
    # 绘制误差收敛比较图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 系统a误差收敛
    ax1.semilogy(range(1, len(errors_jacobi_a)+1), errors_jacobi_a, 
                'o-', label='雅可比方法', linewidth=2, markersize=6)
    ax1.semilogy(range(1, len(errors_gs_a)+1), errors_gs_a, 
                's-', label='高斯-赛德尔方法', linewidth=2, markersize=6)
    ax1.axhline(y=0.001, color='r', linestyle='--', label='容忍度 (0.001)')
    ax1.set_xlabel('迭代次数')
    ax1.set_ylabel('误差 (L∞范数)')
    ax1.set_title('系统a - 误差收敛比较 (对数坐标)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 系统b误差收敛
    ax2.semilogy(range(1, len(errors_jacobi_b)+1), errors_jacobi_b, 
                'o-', label='雅可比方法', linewidth=2, markersize=6)
    ax2.semilogy(range(1, len(errors_gs_b)+1), errors_gs_b, 
                's-', label='高斯-赛德尔方法', linewidth=2, markersize=6)
    ax2.axhline(y=0.001, color='r', linestyle='--', label='容忍度 (0.001)')
    ax2.set_xlabel('迭代次数')
    ax2.set_ylabel('误差 (L∞范数)')
    ax2.set_title('系统b - 误差收敛比较 (对数坐标)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 系统a解收敛过程 - 修复维度问题
    min_iter_a = min(len(solutions_jacobi_a), len(solutions_gs_a), 15)
    iterations_a = range(min_iter_a)
    x1_jacobi_a = [sol[0] for sol in solutions_jacobi_a[:min_iter_a]]
    x2_jacobi_a = [sol[1] for sol in solutions_jacobi_a[:min_iter_a]]
    x3_jacobi_a = [sol[2] for sol in solutions_jacobi_a[:min_iter_a]]
    
    x1_gs_a = [sol[0] for sol in solutions_gs_a[:min_iter_a]]
    x2_gs_a = [sol[1] for sol in solutions_gs_a[:min_iter_a]]
    x3_gs_a = [sol[2] for sol in solutions_gs_a[:min_iter_a]]
    
    ax3.plot(iterations_a, x1_jacobi_a, 'o-', label='雅可比 x1', linewidth=2, markersize=4)
    ax3.plot(iterations_a, x2_jacobi_a, 's-', label='雅可比 x2', linewidth=2, markersize=4)
    ax3.plot(iterations_a, x3_jacobi_a, '^-', label='雅可比 x3', linewidth=2, markersize=4)
    
    ax3.plot(iterations_a, x1_gs_a, 'o--', label='高斯-赛德尔 x1', linewidth=2, markersize=4)
    ax3.plot(iterations_a, x2_gs_a, 's--', label='高斯-赛德尔 x2', linewidth=2, markersize=4)
    ax3.plot(iterations_a, x3_gs_a, '^--', label='高斯-赛德尔 x3', linewidth=2, markersize=4)
    
    ax3.set_xlabel('迭代次数')
    ax3.set_ylabel('解的值')
    ax3.set_title('系统a - 解收敛过程')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 系统b解收敛过程 - 修复维度问题
    min_iter_b = min(len(solutions_jacobi_b), len(solutions_gs_b), 15)
    iterations_b = range(min_iter_b)
    x1_jacobi_b = [sol[0] for sol in solutions_jacobi_b[:min_iter_b]]
    x2_jacobi_b = [sol[1] for sol in solutions_jacobi_b[:min_iter_b]]
    x3_jacobi_b = [sol[2] for sol in solutions_jacobi_b[:min_iter_b]]
    
    x1_gs_b = [sol[0] for sol in solutions_gs_b[:min_iter_b]]
    x2_gs_b = [sol[1] for sol in solutions_gs_b[:min_iter_b]]
    x3_gs_b = [sol[2] for sol in solutions_gs_b[:min_iter_b]]
    
    ax4.plot(iterations_b, x1_jacobi_b, 'o-', label='雅可比 x1', linewidth=2, markersize=4)
    ax4.plot(iterations_b, x2_jacobi_b, 's-', label='雅可比 x2', linewidth=2, markersize=4)
    ax4.plot(iterations_b, x3_jacobi_b, '^-', label='雅可比 x3', linewidth=2, markersize=4)
    
    ax4.plot(iterations_b, x1_gs_b, 'o--', label='高斯-赛德尔 x1', linewidth=2, markersize=4)
    ax4.plot(iterations_b, x2_gs_b, 's--', label='高斯-赛德尔 x2', linewidth=2, markersize=4)
    ax4.plot(iterations_b, x3_gs_b, '^--', label='高斯-赛德尔 x3', linewidth=2, markersize=4)
    
    ax4.set_xlabel('迭代次数')
    ax4.set_ylabel('解的值')
    ax4.set_title('系统b - 解收敛过程')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('problem5_convergence.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 输出最终结果
    print(f"\n系统a结果:")
    print(f"雅可比方法: 迭代{iter_jacobi_a}次, 解: {x_jacobi_a}")
    print(f"高斯-赛德尔方法: 迭代{iter_gs_a}次, 解: {x_gs_a}")
    
    print(f"\n系统b结果:")
    print(f"雅可比方法: 迭代{iter_jacobi_b}次, 解: {x_jacobi_b}")
    print(f"高斯-赛德尔方法: 迭代{iter_gs_b}次, 解: {x_gs_b}")

def main():
    """主函数"""
    print("数值分析作业 - Python 图形生成")
    print("=" * 50)
    
    # 生成所有问题的图形
    plot_problem1()
    plot_problem3() 
    plot_problem4()
    plot_problem5()
    
    print("\n所有图形生成完成！")
    print("生成的文件:")
    print("  - problem1_errors.png (问题1 - 误差分析)")
    print("  - problem3_solutions.png (问题3 - 高斯消元法解)")
    print("  - problem4_iterations.png (问题4 - 雅可比迭代)")
    print("  - problem5_convergence.png (问题5 - 收敛性分析)")

if __name__ == "__main__":
    main()