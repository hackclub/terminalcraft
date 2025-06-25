#include "equation.hpp"

// Parent methods

int64_t Equation::getA(void) const
{
    return this->a;
}

int64_t Equation::getB(void) const
{
    return this->b;
}

int64_t Equation::getC(void) const
{
    return this->c;
}

double Equation::getVertexX(void) const
{
    return -b / 2*a;
}

double Equation::getVertexY(void) const
{
    return evaluate(getVertexX());
}

double Equation::getDiscriminant(void) const
{
    return (b*b) - (4*a*c);
}

double Equation::evaluate(double x) const
{
    return a*x*x + b*x + c;
}

int64_t VertexEquation::getBFromGiven(int64_t a, int64_t h, int64_t k)
{
    return -2*a*h;
}

int64_t VertexEquation::getCFromGiven(int64_t a, int64_t h, int64_t k)
{
    return a*h*h + k;
}

int64_t InterceptEquation::getBFromGiven(int64_t a, int64_t p, int64_t q)
{
    return -a * (p + q);
}

int64_t InterceptEquation::getCFromGiven(int64_t a, int64_t p, int64_t q)
{
    return a*p*q;
}
