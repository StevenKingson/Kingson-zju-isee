#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#define N 3

// 计算向量的无穷范数
double infinity_norm(double x[], int n) {
    double max_val = 0.0;
    for (int i = 0; i < n; i++) {
        if (fabs(x[i]) > max_val) {
            max_val = fabs(x[i]);
        }
    }
    return max_val;
}

// 矩阵向量乘法
void matrix_vector_mult(double A[N][N], double x[], double result[]) {
    for (int i = 0; i < N; i++) {
        result[i] = 0.0;
        for (int j = 0; j < N; j++) {
            result[i] += A[i][j] * x[j];
        }
    }
}

// 向量减法
void vector_subtract(double a[], double b[], double result[], int n) {
    for (int i = 0; i < n; i++) {
        result[i] = a[i] - b[i];
    }
}

void problem1() {
    printf("问题1：计算近似解的误差和残差\n");
    
    double A[N][N] = {{1, 2, 3}, {2, 3, 4}, {3, 4, 6}};
    double b[N] = {1, -1, 2};
    
    // 部分a
    double x_a[N] = {0, -7, 5};
    double xtilde_a[N] = {-0.2, -7.5, 5.4};
    
    double diff_a[N], Ax_a[N], residual_a[N];
    
    vector_subtract(x_a, xtilde_a, diff_a, N);
    matrix_vector_mult(A, xtilde_a, Ax_a);
    vector_subtract(Ax_a, b, residual_a, N);
    
    printf("部分a:\n");
    printf("||x - x_tilde||_∞ = %.6f\n", infinity_norm(diff_a, N));
    printf("||A*x_tilde - b||_∞ = %.6f\n\n", infinity_norm(residual_a, N));
    
    // 部分b
    double x_b[N] = {0, -7, 5};
    double xtilde_b[N] = {-0.33, -7.9, 5.8};
    
    double diff_b[N], Ax_b[N], residual_b[N];
    
    vector_subtract(x_b, xtilde_b, diff_b, N);
    matrix_vector_mult(A, xtilde_b, Ax_b);
    vector_subtract(Ax_b, b, residual_b, N);
    
    printf("部分b:\n");
    printf("||x - x_tilde||_∞ = %.6f\n", infinity_norm(diff_b, N));
    printf("||A*x_tilde - b||_∞ = %.6f\n\n", infinity_norm(residual_b, N));
}

// 高斯消元法带有缩放部分主元选择
void gaussian_elimination_scaled_pivot(int n, double A[n][n], double b[n], double x[n]) {
    // 创建副本以避免修改原始矩阵
    double A_copy[n][n];
    double b_copy[n];
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            A_copy[i][j] = A[i][j];
        }
        b_copy[i] = b[i];
    }
    
    double s[n]; // 缩放因子
    int row_index[n]; // 行索引
    
    // 初始化行索引和缩放因子
    for (int i = 0; i < n; i++) {
        row_index[i] = i;
        s[i] = 0.0;
        for (int j = 0; j < n; j++) {
            if (fabs(A_copy[i][j]) > s[i]) {
                s[i] = fabs(A_copy[i][j]);
            }
        }
    }
    
    // 消元过程
    for (int k = 0; k < n-1; k++) {
        // 选择主元
        double max_ratio = 0.0;
        int max_index = k;
        
        for (int i = k; i < n; i++) {
            int row = row_index[i];
            double ratio = fabs(A_copy[row][k]) / s[row];
            if (ratio > max_ratio) {
                max_ratio = ratio;
                max_index = i;
            }
        }
        
        // 交换行索引
        int temp = row_index[k];
        row_index[k] = row_index[max_index];
        row_index[max_index] = temp;
        
        // 消元
        for (int i = k+1; i < n; i++) {
            int row_i = row_index[i];
            int row_k = row_index[k];
            double m = A_copy[row_i][k] / A_copy[row_k][k];
            
            for (int j = k; j < n; j++) {
                A_copy[row_i][j] -= m * A_copy[row_k][j];
            }
            b_copy[row_i] -= m * b_copy[row_k];
        }
    }
    
    // 回代
    for (int i = n-1; i >= 0; i--) {
        int row = row_index[i];
        x[i] = b_copy[row];
        for (int j = i+1; j < n; j++) {
            x[i] -= A_copy[row][j] * x[j];
        }
        x[i] /= A_copy[row][i];
    }
}

void problem3() {
    printf("问题3：高斯消元法带有缩放部分主元选择\n");
    
    // 系统a
    double A1[2][2] = {{0.03, 58.9}, {5.31, -6.10}};
    double b1[2] = {59.2, 47.0};
    double x1[2];
    
    gaussian_elimination_scaled_pivot(2, A1, b1, x1);
    
    printf("系统a的解:\n");
    printf("x1 = %.6f, x2 = %.6f\n", x1[0], x1[1]);
    
    // 系统b
    double A2[3][3] = {{3.03, -12.1, 14}, {-3.03, 12.1, -7}, {6.11, -14.2, 21}};
    double b2[3] = {-119, 120, -139};
    double x2[3];
    
    gaussian_elimination_scaled_pivot(3, A2, b2, x2);
    
    printf("系统b的解:\n");
    printf("x1 = %.6f, x2 = %.6f, x3 = %.6f\n\n", x2[0], x2[1], x2[2]);
}

// 雅可比迭代一步
void jacobi_iteration(int n, double A[n][n], double b[n], double x_old[n], double x_new[n]) {
    for (int i = 0; i < n; i++) {
        x_new[i] = b[i];
        for (int j = 0; j < n; j++) {
            if (j != i) {
                x_new[i] -= A[i][j] * x_old[j];
            }
        }
        x_new[i] /= A[i][i];
    }
}

void problem4() {
    printf("问题4：雅可比迭代法\n");
    
    // 系统a
    double A3[3][3] = {{4, 1, -1}, {-1, 3, 1}, {2, 2, 5}};
    double b3[3] = {5, -4, 1};
    double x0[3] = {0, 0, 0};
    double x1[3], x2[3], x3[3];
    
    jacobi_iteration(3, A3, b3, x0, x1);
    jacobi_iteration(3, A3, b3, x1, x2);
    jacobi_iteration(3, A3, b3, x2, x3);
    
    printf("系统a的前三次迭代结果:\n");
    printf("第一次: %.6f, %.6f, %.6f\n", x1[0], x1[1], x1[2]);
    printf("第二次: %.6f, %.6f, %.6f\n", x2[0], x2[1], x2[2]);
    printf("第三次: %.6f, %.6f, %.6f\n", x3[0], x3[1], x3[2]);
    
    // 系统b
    double A4[3][3] = {{-2, 1, 0.5}, {1, -2, -0.5}, {0, 1, 2}};
    double b4[3] = {4, -4, 0};
    double y0[3] = {0, 0, 0};
    double y1[3], y2[3], y3[3];
    
    jacobi_iteration(3, A4, b4, y0, y1);
    jacobi_iteration(3, A4, b4, y1, y2);
    jacobi_iteration(3, A4, b4, y2, y3);
    
    printf("系统b的前三次迭代结果:\n");
    printf("第一次: %.6f, %.6f, %.6f\n", y1[0], y1[1], y1[2]);
    printf("第二次: %.6f, %.6f, %.6f\n", y2[0], y2[1], y2[2]);
    printf("第三次: %.6f, %.6f, %.6f\n\n", y3[0], y3[1], y3[2]);
}

// 计算两个向量的无穷范数差值
double vector_diff_infinity_norm(double x[], double y[], int n) {
    double max_diff = 0.0;
    for (int i = 0; i < n; i++) {
        double diff = fabs(x[i] - y[i]);
        if (diff > max_diff) {
            max_diff = diff;
        }
    }
    return max_diff;
}

// 雅可比方法
void jacobi_method(int n, double A[n][n], double b[n], double tol, int max_iter, double x[]) {
    double x_old[n];
    double x_new[n];
    
    // 初始化为0
    for (int i = 0; i < n; i++) {
        x_old[i] = 0.0;
        x_new[i] = 0.0;
    }
    
    for (int k = 0; k < max_iter; k++) {
        jacobi_iteration(n, A, b, x_old, x_new);
        
        if (vector_diff_infinity_norm(x_new, x_old, n) < tol) {
            break;
        }
        
        // 更新
        for (int i = 0; i < n; i++) {
            x_old[i] = x_new[i];
        }
    }
    
    // 复制结果
    for (int i = 0; i < n; i++) {
        x[i] = x_new[i];
    }
}

// 高斯-赛德尔迭代一步
void gauss_seidel_iteration(int n, double A[n][n], double b[n], double x[]) {
    for (int i = 0; i < n; i++) {
        double sum = b[i];
        for (int j = 0; j < n; j++) {
            if (j != i) {
                sum -= A[i][j] * x[j];
            }
        }
        x[i] = sum / A[i][i];
    }
}

// 高斯-赛德尔方法
void gauss_seidel_method(int n, double A[n][n], double b[n], double tol, int max_iter, double x[]) {
    double x_old[n];
    
    // 初始化为0
    for (int i = 0; i < n; i++) {
        x[i] = 0.0;
        x_old[i] = 0.0;
    }
    
    for (int k = 0; k < max_iter; k++) {
        // 保存旧值
        for (int i = 0; i < n; i++) {
            x_old[i] = x[i];
        }
        
        gauss_seidel_iteration(n, A, b, x);
        
        if (vector_diff_infinity_norm(x, x_old, n) < tol) {
            break;
        }
    }
}

void problem5() {
    printf("问题5：雅可比方法和高斯-赛德尔方法\n");
    double tol = 0.001;
    int max_iter = 1000;
    
    // 系统a
    double A5a[3][3] = {{3, -1, 1}, {3, 6, 2}, {3, 3, 7}};
    double b5a[3] = {1, 0, 4};
    double x_jacobi_a[3], x_gs_a[3];
    
    jacobi_method(3, A5a, b5a, tol, max_iter, x_jacobi_a);
    gauss_seidel_method(3, A5a, b5a, tol, max_iter, x_gs_a);
    
    printf("系统a的雅可比方法解:\n");
    printf("x1 = %.6f, x2 = %.6f, x3 = %.6f\n", x_jacobi_a[0], x_jacobi_a[1], x_jacobi_a[2]);
    printf("系统a的高斯-赛德尔方法解:\n");
    printf("x1 = %.6f, x2 = %.6f, x3 = %.6f\n", x_gs_a[0], x_gs_a[1], x_gs_a[2]);
    
    // 系统b
    double A5b[3][3] = {{10, -1, 0}, {-1, 10, -2}, {0, -2, 10}};
    double b5b[3] = {9, 7, 6};
    double x_jacobi_b[3], x_gs_b[3];
    
    jacobi_method(3, A5b, b5b, tol, max_iter, x_jacobi_b);
    gauss_seidel_method(3, A5b, b5b, tol, max_iter, x_gs_b);
    
    printf("系统b的雅可比方法解:\n");
    printf("x1 = %.6f, x2 = %.6f, x3 = %.6f\n", x_jacobi_b[0], x_jacobi_b[1], x_jacobi_b[2]);
    printf("系统b的高斯-赛德尔方法解:\n");
    printf("x1 = %.6f, x2 = %.6f, x3 = %.6f\n\n", x_gs_b[0], x_gs_b[1], x_gs_b[2]);
}

int main() {
    printf("数值分析作业3 - C语言实现\n");
    printf("==========================\n\n");
    
    problem1();
    problem3();
    problem4();
    problem5();
    
    printf("程序执行完毕！\n");
    return 0;
}