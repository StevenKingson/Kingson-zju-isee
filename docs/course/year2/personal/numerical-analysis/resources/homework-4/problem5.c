#include <stdio.h>
#include <stdbool.h>

// The proposed spline function S(x) = x
double S(double x) {
    return x;
}

// First derivative S'(x) = 1
double Sp(double x) {
    return 1.0;
}

// Second derivative S''(x) = 0
double Spp(double x) {
    return 0.0;
}

int main() {
    printf("--- Problem 5: Cubic Spline ---\n\n");
    printf("Proposed Spline Function: S(x) = x\n\n");
    
    double x_nodes[] = {0.0, 1.0, 2.0};
    double y_nodes[] = {0.0, 1.0, 2.0};
    int n = 2; // Number of intervals

    // --- 1. Verify Natural Cubic Spline Conditions ---
    printf("--- Verifying Natural Cubic Spline Conditions ---\n");
    bool conditions_met = true;

    // a) Interpolation conditions
    printf("Checking interpolation conditions...\n");
    for (int i = 0; i <= n; i++) {
        if (S(x_nodes[i]) != y_nodes[i]) {
            printf("  S(%f) = %f != %f. FAILED.\n", x_nodes[i], S(x_nodes[i]), y_nodes[i]);
            conditions_met = false;
        } else {
            printf("  S(%f) = %f. PASSED.\n", x_nodes[i], S(x_nodes[i]));
        }
    }

    // b) Continuity of S, S', S'' at internal knots (x=1)
    // For S(x)=x, continuity is inherent.
    printf("Continuity of S, S', S'' at x=1 is inherent as S(x) is a single polynomial. PASSED.\n");

    // c) Natural boundary conditions S''(x0)=0, S''(xn)=0
    printf("Checking natural boundary conditions...\n");
    if (Spp(x_nodes[0]) == 0 && Spp(x_nodes[n]) == 0) {
        printf("  S''(0)=%f, S''(2)=%f. PASSED.\n", Spp(x_nodes[0]), Spp(x_nodes[n]));
    } else {
        printf("  Boundary conditions failed. FAILED.\n");
        conditions_met = false;
    }

    if (conditions_met) {
        printf("Conclusion: S(x) = x is the correct Natural Cubic Spline.\n\n");
    }

    // --- 2. Verify Clamped Cubic Spline Conditions ---
    printf("--- Verifying Clamped Cubic Spline Conditions ---\n");
    conditions_met = true;
    double f_prime_0 = 1.0;
    double f_prime_n = 1.0;

    // Conditions a) and b) are the same as above and have passed.
    printf("Interpolation and continuity conditions passed.\n");
    
    // c) Clamped boundary conditions S'(x0)=1, S'(xn)=1
    printf("Checking clamped boundary conditions...\n");
    if (Sp(x_nodes[0]) == f_prime_0 && Sp(x_nodes[n]) == f_prime_n) {
        printf("  S'(0)=%f, S'(2)=%f. PASSED.\n", Sp(x_nodes[0]), Sp(x_nodes[n]));
    } else {
        printf("  Boundary conditions failed. FAILED.\n");
        conditions_met = false;
    }

    if (conditions_met) {
        printf("Conclusion: S(x) = x is the correct Clamped Cubic Spline.\n");
    }

    return 0;
}