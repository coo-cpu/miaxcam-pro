#include <stdio.h>

double midpoint(long long a, long long b)
{ /*试试看9007199254740993 900719925474099340,输出 9007199254740992.000000浮点数不是万能的*/
    return (a + b) / 2.0;
}
int main(void)
{
    long long x, y;
    scanf("%lld %lld", &x, &y);
    printf("%lf\n", midpoint(x, y));
    return 0;
}