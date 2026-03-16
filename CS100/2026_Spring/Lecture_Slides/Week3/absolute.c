#include <stdio.h>

int abs_int(int);

int main(void)
{
    int x;
    scanf("%d", &x);
    int c = abs_int(x);
    printf("%d", c);
    return 0;
}

int abs_int(int x)
{
    if (x < 0)
        return -x; // 满足就直接退出了
    // 如果走到这一步，说明 x 肯定 >= 0，不需要再写 else if
    return x;
}