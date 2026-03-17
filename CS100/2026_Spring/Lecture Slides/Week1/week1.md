### scanf printf

```c
#include <stdio.h>

int main(void) {
    char name[30];
    int age;
    float num;
    printf("请输入名字和年龄还有一个至少三位小数的浮点数\n");
    scanf("%*s Age:%d %f", &age,&num);
    printf(" %d %.2f\n",age,num);
    return 0;
}
```

### mathmetical function

```c
#include <stdio.h>

double f(double x, double y)
{
    double xy = x * y;
    return xy;
}

int main(void)
{
    double ans = f(2, 2.5);
    printf("%lf\n", ans);
    return 0;
}
```

### 函数调用

```c
#include<stdio.h>

int max(int a, int b){
    if(a < b){   /*注意判断条件要加括号，同时if和else之中的内容也要用大括号包起来*/
        return b;
        }
    else{
        return a;
        }
}

int main(void){
    int a,b;
    scanf("%d%d\n", &a, &b);
    printf("max is %d", max(a, b));
    return 0;
}
```
