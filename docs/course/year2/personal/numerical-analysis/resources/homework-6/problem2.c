#include <stdio.h>
#include <math.h>

// Function definition for part a
double f_a(double x) {
    return exp(x) - x*x + 3*x - 2;
}

// Function definition for part b
double f_b(double x) {
    return x * cos(x) - 2*x*x + 3*x - 1;
}

// Bisection method implementation
void bisection(char id, double a, double b, double tol, double (*f)(double)) {
    if (f(a) * f(b) >= 0) {
        printf("Bisection method fails. f(a) and f(b) must have opposite signs.\n");
        return;
    }

    double p = a;
    int i = 1;

    printf("\n--- Bisection for Problem %c on [%.1f, %.1f] ---\n", id, a, b);
    printf("Iteration\tMidpoint (p)\n");
    printf("--------------------------------------\n");

    while ((b - a) / 2 > tol) {
        p = a + (b - a) / 2; // Avoids potential overflow with (a+b)/2
        printf("%-10d\t%.10f\n", i, p);

        if (f(p) == 0.0) {
            break; // Found exact root
        }

        if (f(a) * f(p) < 0) {
            b = p;
        } else {
            a = p;
        }
        i++;
    }
    printf("--------------------------------------\n");
    printf("Approximate solution is p = %.10f\n", p);
}

int main() {
    double tol = 1e-5;

    // Problem a
    bisection('a', 0.0, 1.0, tol, f_a);

    // Problem b
    bisection('b', 0.2, 0.3, tol, f_b);
    bisection('b', 1.2, 1.3, tol, f_b);
    
    return 0;
}