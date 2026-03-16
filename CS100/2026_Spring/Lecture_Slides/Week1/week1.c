/*一个四则运算器*/
#include <stdio.h>
#include <math.h>

double op_sel(double a, char op, double b)
{
    if (op == '+')
    {
        return a + b;
    }
    else if (op == '-')
    {
        return a - b;
    }
    else if (op == '*')
    {
        return a * b;
    }
    else if (op == '/' && b == 0)
    {
        return NAN;
    }
    else if (op == '/' && b != 0)
    {
        return a / b;
    }
    else
    {
        return NAN;
    }
}
int main(void)
{
    char op;
    double a, b, c;
    printf("Please type in the equation:");
    scanf("%lf %c%lf", &a, &op, &b); /*在%c前面加上一个空格可以跳过所有的whitespace*/
    c = op_sel(a, op, b);
    if (isnan(c))
    {
        printf("Not a valid equation!");
    }
    else
    {
        printf("Result is %lf.\n", c);
    }
    return 0;
}