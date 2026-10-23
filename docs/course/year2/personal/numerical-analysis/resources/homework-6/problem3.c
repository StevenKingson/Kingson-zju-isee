#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// g(x) for part a
double g_a(double x) {
    // x = 1 + (1/PI) * asin(x/2)
    return 1.0 + (1.0 / M_PI) * asin(x / 2.0);
}

// g(x) for part b
double g_b(double x) {
    // x = sqrt(e^x / 3)
    return sqrt(exp(x) / 3.0);
}

// Fixed-point iteration implementation
void fixed_point(char id, double p0, double tol, int max_iter, double (*g)(double)) {
    double p = p0;
    int i = 1;

    printf("\n--- Fixed-Point Iteration for Problem %c ---\n", id);
    printf("Initial guess p0 = %.2f\n", p0);
    printf("Iteration\tp_n\n");
    printf("---------------------------\n");

    while (i <= max_iter) {
        p = g(p0);
        printf("%-10d\t%.8f\n", i, p);

        if (fabs(p - p0) < tol) {
            printf("---------------------------\n");
            printf("Solution found: p = %.8f\n", p);
            return;
        }

        p0 = p;
        i++;
    }

    printf("Method failed after %d iterations.\n", max_iter);
}


int main() {
    double tol = 1e-2;
    int max_iterations = 50;

    // Problem a
    fixed_point('a', 1.0, tol, max_iterations, g_a);

    // Problem b
    fixed_point('b', 1.0, tol, max_iterations, g_b);

    return 0;
}