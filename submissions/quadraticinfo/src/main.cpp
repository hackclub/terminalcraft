#include "main.hpp"

inline void setCursorPos(uint32_t x, uint32_t y)
{
    printf(ESC "[%d;%dH", y, x);
}

inline int calculateRealY(uint32_t vertexY, bool openDir)
{
    return round(vertexY) - (GRAPH_HEIGHT / 2) + (openDir ? OPEN_OFFSET : -OPEN_OFFSET);
}

bool printGraphChar(double realY, double evalY)
{
    bool errorDirection = evalY > realY;
    double error = abs(evalY - realY);

    if (error < 1) printf("▓");
    else if (error < 2) printf("▒");
    else if (error < 3) printf("░");

    return error < 3;
}

int main(void)
{
    std::shared_ptr<Equation> equation;

    printf(ESC "[?1049h"); // Set alternate buffer
    setCursorPos(1, 1);

    #if defined(_WIN32) || defined(_WIN64)
    SetConsoleOutputCP(CP_UTF8);
    #endif

    EquationType type = EQUATION_INVALID;
    printf(LABEL("Enter Equation Type") "(0:Standard, 1:Vertex, 2:Intercept): ");

    while (type == EQUATION_INVALID)
    {
        int inputType;
        scanf("%d", &inputType);
        switch (inputType)
        {
            case 0:
                type = EQUATION_STANDARD;
                break;
            case 1:
                type = EQUATION_VERTEX;
                break;
            case 2:
                type = EQUATION_INTERCEPT;
                break;
            default:
                setCursorPos(1, 1);
                printf(ESC "[2J" LABEL("Invalid type, try again") "(0:Standard, 1:Vertex, 2:Intercept): ");
                break;
        }
    }

    {
        int64_t a, b, c, h, k, p, q;
        switch (type)
        {
            case EQUATION_STANDARD:
                printf(LABEL("Equation") "y = ax^2 + bx + c\n");

                printf("Enter a: ");
                scanf("%" PRId64, &a);
                printf("Enter b: ");
                scanf("%" PRId64, &b);
                printf("Enter c: ");
                scanf("%" PRId64, &c);

                equation = std::make_shared<StandardEquation>(a, b, c);
                break;
            case EQUATION_VERTEX:
                printf(LABEL("Equation") "y = a(x - h)^2 + k\n");

                printf("Enter a: ");
                scanf("%" PRId64, &a);
                printf("Enter h: ");
                scanf("%" PRId64, &h);
                printf("Enter k: ");
                scanf("%" PRId64, &k);

                equation = std::make_shared<VertexEquation>(a, h, k);
                break;
            case EQUATION_INTERCEPT:
                printf(LABEL("Equation") "y = a(x - p)(x - q)\n");

                printf("Enter a: ");
                scanf("%" PRId64, &a);
                printf("Enter p: ");
                scanf("%" PRId64, &p);
                printf("Enter q: ");
                scanf("%" PRId64, &q);

                equation = std::make_shared<InterceptEquation>(a, p, q);
                break;
            default:
                printf("Invalid type.");
                exit(type);
                break;
        }
    }

    // Print information

    printf("\n");

    printf(LABEL("Equation (Standard Form)") "y = " "%" PRId64 "x^2 + " "%" PRId64 "x + " "%" PRId64 "\n", equation->getA(), equation->getB(), equation->getC());

    double discriminant = equation->getDiscriminant();
    printf(LABEL("Discriminant") "%f ", discriminant);

    if (discriminant > 0) printf("(Solutions: 2)\n");
    else if (discriminant == 0) printf("(Solutions: 1)\n");
    else if (discriminant < 0) printf("(Solutions: 0)\n");

    printf("\n" LABEL("Solutions") "\n");
    if (discriminant > 0)
    {
        double numeratorSqrt = sqrt(discriminant);
        double denomenator = 2*equation->getA();

        printf(LABEL("x1") "%f\n", (-equation->getB() + numeratorSqrt) / denomenator);
        printf(LABEL("x2") "%f\n", (-equation->getB() - numeratorSqrt) / denomenator);
    } else if (discriminant == 0)
    {
        double numeratorSqrt = sqrt(discriminant);
        double denomenator = 2*equation->getA();

        printf(LABEL("x1") ": %f\n", (-equation->getB() + numeratorSqrt) / denomenator);
    } else if (discriminant < 0) printf("Solutions are imaginary\n");

    printf("\n" LABEL("Graph Information") "\n");

    double vertX = equation->getVertexX();
    double vertY = equation->getVertexY();
    printf(LABEL("Line of Symmetry") "x = %f\n", vertX);
    printf(LABEL("Vertex") "(%f, %f)\n", vertX, vertY);

    bool opensUp = equation->getA() > 0;
    printf(LABEL("Direction") "Opens %s\n", opensUp ? "Up" : "Down");

    printf("\nPress enter to exit...");
    printf(ESC "[s"); // Save cursor position

    // Print graph

    setCursorPos(GRAPH_OFFSET_X, GRAPH_OFFSET_Y);

    int64_t realX = round(vertX) - (GRAPH_WIDTH / 2);
    int64_t realY = calculateRealY(vertY, opensUp);
    for (int x = 0; x < GRAPH_WIDTH; x++)
    {
        for (int y = 0; y < GRAPH_HEIGHT; y++)
        {
            setCursorPos(GRAPH_OFFSET_X + x, GRAPH_OFFSET_Y + GRAPH_HEIGHT - y);

            double evalY = equation->evaluate(realX);

            printf(ESC "[31m");
            if (printGraphChar(realY, evalY));
            else {
                printf(ESC "[32m");
                if (realX == 0 && realY == 0) printf("┼");
                else if (realX == 0) {
                    printf("│");
                    if (y == 0) printf(ESC "[2B" ESC "[1D" "0");
                }
                else if (realY == 0) {
                    printf("─");
                    if (x == GRAPH_WIDTH - 1) printf("  0");
                }
            }
            realY++;
        }
        setCursorPos(GRAPH_OFFSET_X + x, GRAPH_OFFSET_Y);

        realX++;
        realY = calculateRealY(vertY, opensUp);
    }

    printf(ESC "[0m");

    // Wait for enter

    printf(ESC "[u"); // Return to saved cursor position
    getchar();
    getchar();

    printf(ESC "[?1049l"); // Return main buffer

    return 0;
}
