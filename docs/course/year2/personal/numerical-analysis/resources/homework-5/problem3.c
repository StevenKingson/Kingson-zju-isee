#include <stdio.h>
#include <math.h>

// Define the functions for integration
double f_a(double x) { return pow(cos(x), 2); }
double f_b(double x) { return x * log(x + 1); }
double f_c(double x) { return pow(sin(x) - 1, 2); }
double f_d(double x) { return 1 / (x * log(x)); }

// Structure to hold integral information
typedef struct {
    char id;
    double a;
    double b;
    double (*func)(double);
} Integral;

// Trapezoidal Rule
double trapezoidal(Integral I) {
    return (I.b - I.a) / 2.0 * (I.func(I.a) + I.func(I.b));
}

// Simpson's Rule
double simpsons(Integral I) {
    double mid = (I.a + I.b) / 2.0;
    return (I.b - I.a) / 6.0 * (I.func(I.a) + 4 * I.func(mid) + I.func(I.b));
}

int main() {
    Integral integrals[] = {
        {'a', -0.25, 0.25, f_a},
        {'b', -0.5,  0.0,  f_b},
        {'c', 0.75,  1.3,  f_c},
        {'d', M_E,   M_E + 1.0, f_d}
    };

    int num_integrals = sizeof(integrals) / sizeof(integrals[0]);

    printf("--- Approximations for Integrals ---\n");
    for (int i = 0; i < num_integrals; i++) {
        printf("\nIntegral (%c):\n", integrals[i].id);
        printf("  Trapezoidal Rule: %f\n", trapezoidal(integrals[i]));
        printf("  Simpson's Rule:   %f\n", simpsons(integrals[i]));
    }

    return 0;
}