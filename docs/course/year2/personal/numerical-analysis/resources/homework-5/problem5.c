#include <stdio.h>

// Differential equation for part a
double ivp_a(double t, double y) {
    if (t == 0) return 0; // Avoid division by zero
    return (y / t) - pow(y / t, 2);
}

// Differential equation for part b
double ivp_b(double t, double y) {
    if (t == 0) return 1; // Avoid division by zero
    return 1 + (y / t) + pow(y / t, 2);
}

// Euler's method implementation
void euler_method(char id, double t_start, double t_end, double h, double w0, double (*f)(double, double)) {
    double w = w0;
    double t = t_start;

    printf("--- Euler's Method Results for IVP (%c) ---\n", id);
    printf("t_i       w_i\n");
    printf("------------------\n");
    printf("%-10.2f%-10.6f\n", t, w);

    while (t < t_end) {
        w = w + h * f(t, w);
        t = t + h;
        printf("%-10.2f%-10.6f\n", t, w);
    }
}

int main() {
    // Problem a
    euler_method('a', 1.0, 2.0, 0.1, 1.0, ivp_a);

    printf("\n");

    // Problem b
    euler_method('b', 1.0, 3.0, 0.2, 0.0, ivp_b);

    return 0;
}