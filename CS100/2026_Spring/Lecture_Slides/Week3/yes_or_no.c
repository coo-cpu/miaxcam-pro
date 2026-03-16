#include <stdio.h>

int yes_or_no(void)
{
    char judge;
    while (1)
    {
        scanf(" %c", &judge);
        if (judge == 'Y' || judge == 'y')
        {
            return 1;
        }
        else if (judge == 'N' || judge == 'n')
        {
            return 0;
        }
        else
        {
            printf("Invalid Input, Try again. \n");
        }
    }
}

int main(void)
{
    int response = yes_or_no();
    if (response)
        printf("Your response is yes.\n");
    else
        printf("Your response is no.\n");
    return 0;
}
