#include <cstdio>
#include <cmath>

#define LABEL(text) "\x1b[32m" text "\x1b[0m"

int main(void)
{
    int a;
    int b;
    int c;

    printf(LABEL("Equation") ": y = ax^2 + bx + c\n");

    printf("Enter a: ");
    scanf("%d", &a);
    printf("Enter b: ");
    scanf("%d", &b);
    printf("Enter c: ");
    scanf("%d", &c);

    printf(LABEL("=== QUADRATIC EQUATION INFORMATION ===") "\n\n");

    printf(LABEL("Equation") ": y = %dx^2 + %dx + %d\n", a, b, c);

    double discriminant = (b*b) - (4*a*c);
    printf(LABEL("Discriminant") ": %f ", discriminant);

    if (discriminant > 0) printf("(Solutions: 2)\n");
    else if (discriminant == 0) printf("(Solutions: 1)\n");
    else if (discriminant < 0) printf("(Solutions: 0)\n");

    printf("\n" LABEL("== Solutions ==") "\n");
    if (discriminant > 0)
    {
        double numeratorSqrt = sqrt(discriminant);
        double denomenator = 2*a;

        printf(LABEL("x1") ": %f\n", (-b + numeratorSqrt) / denomenator);
        printf(LABEL("x2") ": %f\n", (-b - numeratorSqrt) / denomenator);
    } else if (discriminant == 0)
    {
        double numeratorSqrt = sqrt(discriminant);
        double denomenator = 2*a;

        printf(LABEL("x1") ": %f\n", (-b + numeratorSqrt) / denomenator);
    } else if (discriminant < 0) printf("Solutions are imaginary\n");

    printf("\n" LABEL("== Graph Information ==") "\n");

    double x = (-b) / (2*a);
    double y = a*x*x + b*x + c;
    printf(LABEL("Line of Symmetry") ": x = %f\n", x);
    printf(LABEL("Vertex") ": (%f, %f)\n", x, y);

    bool opensUp = a > 0;
    printf(LABEL("Direction") ": Opens %s\n", opensUp ? "Up" : "Down");

    return 0;
}
