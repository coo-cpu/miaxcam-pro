#include <stdio.h>

int main(void)
{
    char op;
    double a = 0.0, b = 0.0;
    scanf("%lf %c%lf", &a, &op, &b);
    switch (op)
    {
    case '+':
        printf(" %lf + %lf = %lf\n", a, b, a + b);
        break;
    case '-':
        printf("%lf - %lf = %lf\n", a, b, a - b);
        break;
    case '*':
        printf("%lf * %lf = %lf\n", a, b, a * b);
        break;
    case '/':
        printf("%lf / %lf = %lf\n", a, b, a / b);
        break;
    default:
        printf("Invalid operator!\n");
        break;
    }
    return 0;
}