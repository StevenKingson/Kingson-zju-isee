#include <stdio.h>
#include <math.h>

// Part a: f(x) = e^(2x) * cos(3x)
double f_a(double x) {
    return exp(2 * x) * cos(3 * x);
}

// Third derivative of f_a(x)
double dddf_a(double x) {
    return exp(2 * x) * (-46 * cos(3 * x) - 9 * sin(3 * x));
}

// Part b: f(x) = sin(ln(x))
double f_b(double x) {
    return sin(log(x));
}

// Third derivative of f_b(x)
double dddf_b(double x) {
    return (cos(log(x)) + 3 * sin(log(x))) / (x * x * x);
}

// Lagrange basis polynomial L_i(x) for n=2
double lagrange_basis(double x, int i, double* x_nodes) {
    double result = 1.0;
    for (int j = 0; j <= 2; j++) {
        if (i != j) {
            result *= (x - x_nodes[j]) / (x_nodes[i] - x_nodes[j]);
        }
    }
    return result;
}

// Lagrange interpolating polynomial P_2(x)
double lagrange_poly(double x, double* x_nodes, double* y_nodes) {
    double result = 0.0;
    for (int i = 0; i <= 2; i++) {
        result += y_nodes[i] * lagrange_basis(x, i, x_nodes);
    }
    return result;
}

// Function to find the error bound
void find_error_bound(double x0, double xn, double* x_nodes, double (*dddf)(double)) {
    double max_w = 0.0;
    double max_dddf = 0.0;
    int steps = 1000;
    double step_size = (xn - x0) / steps;

    for (int i = 0; i <= steps; i++) {
        double x = x0 + i * step_size;
        double w_val = fabs((x - x_nodes[0]) * (x - x_nodes[1]) * (x - x_nodes[2]));
        if (w_val > max_w) {
            max_w = w_val;
        }

        double dddf_val = fabs(dddf(x));
        if (dddf_val > max_dddf) {
            max_dddf = dddf_val;
        }
    }
    
    double error_bound = (max_w * max_dddf) / 6.0; // 3! = 6
    printf("Max |(x-x0)(x-x1)(x-x2)| on [%.1f, %.1f] is approx: %f\n", x0, xn, max_w);
    printf("Max |f'''(x)| on [%.1f, %.1f] is approx: %f\n", x0, xn, max_dddf);
    printf("The absolute error bound is approx: %f\n", error_bound);
}


int main() {
    // --- Problem 1a ---
    printf("--- Problem 1a: f(x) = e^(2x) * cos(3x) ---\n");
    double x_nodes_a[] = {0.0, 0.3, 0.6};
    double y_nodes_a[3];
    for (int i = 0; i < 3; i++) {
        y_nodes_a[i] = f_a(x_nodes_a[i]);
    }
    
    printf("Data points (x, y):\n");
    for (int i = 0; i < 3; i++) {
        printf("(%f, %f)\n", x_nodes_a[i], y_nodes_a[i]);
    }
    
    // The polynomial itself is a sum of the basis polynomials.
    // P2(x) = y0*L0(x) + y1*L1(x) + y2*L2(x)
    printf("The Lagrange interpolating polynomial is constructed using these points.\n");
    printf("For example, P2(0.15) = %f\n", lagrange_poly(0.15, x_nodes_a, y_nodes_a));
    
    find_error_bound(0.0, 0.6, x_nodes_a, dddf_a);
    
    printf("\n");
    
    // --- Problem 1b ---
    printf("--- Problem 1b: f(x) = sin(ln(x)) ---\n");
    double x_nodes_b[] = {2.0, 2.4, 2.6};
    double y_nodes_b[3];
    for (int i = 0; i < 3; i++) {
        y_nodes_b[i] = f_b(x_nodes_b[i]);
    }

    printf("Data points (x, y):\n");
    for (int i = 0; i < 3; i++) {
        printf("(%f, %f)\n", x_nodes_b[i], y_nodes_b[i]);
    }
    
    printf("The Lagrange interpolating polynomial is constructed using these points.\n");
    printf("For example, P2(2.2) = %f\n", lagrange_poly(2.2, x_nodes_b, y_nodes_b));

    find_error_bound(2.0, 2.6, x_nodes_b, dddf_b);

    return 0;
}