#include <stdio.h>
#include <math.h>

// Functions from previous problem
double f_a_r(double x) { return pow(cos(x), 2); }
double f_b_r(double x) { return x * log(x + 1); }
double f_c_r(double x) { return pow(sin(x) - 1, 2); }
double f_d_r(double x) { return 1 / (x * log(x)); }

// Helper for composite trapezoidal rule
double composite_trapezoidal(double a, double b, int n, double (*func)(double)) {
    double h = (b - a) / n;
    double sum = 0.5 * (func(a) + func(b));
    for (int i = 1; i < n; i++) {
        sum += func(a + i * h);
    }
    return h * sum;
}

// Romberg integration to compute R(3,3)
void compute_r33(char id, double a, double b, double (*func)(double)) {
    double R[4][4] = {0}; // Using 1-based indexing for clarity

    // First column: Trapezoidal
    R[1][1] = composite_trapezoidal(a, b, 1, func);
    R[2][1] = composite_trapezoidal(a, b, 2, func);
    R[3][1] = composite_trapezoidal(a, b, 4, func);

    // Second column
    R[2][2] = (4.0 * R[2][1] - R[1][1]) / 3.0;
    R[3][2] = (4.0 * R[3][1] - R[2][1]) / 3.0;

    // Third column
    R[3][3] = (16.0 * R[3][2] - R[2][2]) / 15.0;
    
    printf("Integral (%c): R_3,3 = %f\n", id, R[3][3]);
}

int main() {
    printf("--- Romberg Integration Results ---\n");
    compute_r33('a', -1.0, 1.0, f_a_r);
    compute_r33('b', -0.75, -0.75, f_b_r); // Note: limits are the same, integral is 0
    compute_r33('c', 1.0, 4.0, f_c_r);
    compute_r33('d', M_E, 2.0 * M_E, f_d_r);

    return 0;
}