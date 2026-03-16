#include <stdio.h>

int main(void)
{
    char c;
    char uppercase;
    scanf(" %c", &c);
    uppercase = (c >= 'a' && c <= 'z') ? c - ('a' - 'A') : c;
    printf("%c", uppercase);
    return 0;
}