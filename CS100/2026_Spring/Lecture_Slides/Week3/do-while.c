#include <stdio.h>

int main(void)
{
    int i = 0, sum = 0, x;
    int n;
    scanf("%d", &n);
    do
    {
        scanf("%d", &x);
        sum += x;
        i++;
        // printf("%d\n", sum);
    } while (i < n);
    printf("%d\n", sum);
    return 0;
}