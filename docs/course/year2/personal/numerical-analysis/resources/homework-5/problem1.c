#include <stdio.h>

// Function to calculate derivatives for a given table of data
void calculate_derivatives(double x[], double fx[], int n) {
    double h = x[1] - x[0];
    double dfx;

    printf("Results for x values:\n");

    // Start point
    dfx = (-3 * fx[0] + 4 * fx[1] - fx[2]) / (2 * h);
    printf("f'(%0.1f) = %f\n", x[0], dfx);

    // Midpoints
    for (int i = 1; i < n - 1; i++) {
        dfx = (fx[i + 1] - fx[i - 1]) / (2 * h);
        printf("f'(%0.1f) = %f\n", x[i], dfx);
    }

    // End point
    dfx = (fx[n - 3] - 4 * fx[n - 2] + 3 * fx[n - 1]) / (2 * h);
    printf("f'(%0.1f) = %f\n", x[n - 1], dfx);
}

int main() {
    // Data for Table a
    double x_a[] = {1.1, 1.2, 1.3, 1.4};
    double fx_a[] = {9.025013, 11.02318, 13.46374, 16.44465};
    printf("--- Table a ---\n");
    calculate_derivatives(x_a, fx_a, 4);

    printf("\n");

    // Data for Table b
    double x_b[] = {8.1, 8.3, 8.5, 8.7};
    double fx_b[] = {16.94410, 17.56492, 18.19056, 18.82091};
    printf("--- Table b ---\n");
    calculate_derivatives(x_b, fx_b, 4);

    return 0;
}