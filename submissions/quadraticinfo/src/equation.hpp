#pragma once

#include <cstdint>

enum EquationType
{
    EQUATION_STANDARD,
    EQUATION_VERTEX,
    EQUATION_INTERCEPT,
    EQUATION_INVALID
};

class Equation
{
    private:
        int64_t a, b, c;
    public:
        Equation(int64_t a, int64_t b, int64_t c) : a(a), b(b), c(c) {}

        int64_t getA(void) const;
        int64_t getB(void) const;
        int64_t getC(void) const;
        double getVertexX(void) const;
        double getVertexY(void) const;
        double getDiscriminant(void) const;

        double evaluate(double x) const;
};

class StandardEquation : public Equation
{
    public:
        StandardEquation(int64_t a, int64_t b, int64_t c) : Equation(a, b, c) {}
};

class VertexEquation : public Equation
{
    private:
        int64_t getBFromGiven(int64_t a, int64_t h, int64_t k);
        int64_t getCFromGiven(int64_t a, int64_t h, int64_t k);
    public:
        VertexEquation(int64_t a, int64_t h, int64_t k) : Equation(a, getBFromGiven(a, h, k), getCFromGiven(a, h, k)) {}
};

class InterceptEquation : public Equation
{
    private:
        int64_t getBFromGiven(int64_t a, int64_t p, int64_t q);
        int64_t getCFromGiven(int64_t a, int64_t p, int64_t q);
    public:
        InterceptEquation(int64_t a, int64_t p, int64_t q) : Equation(a, getBFromGiven(a, p, q), getCFromGiven(a, p, q)) {}
};
