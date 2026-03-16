### Technical terminology

1. machine code(机器语言) : codes that computers can only read, which is binary.
2. Assembly code(汇编语言) : codes that are made for human-readability.
3. High-level languages(高级程序语言):  C，C++，Python
4. Compiler（编译器）：所有源代码全部转化成机器语言之后再开始运行。
5. Interpreter (解释器) ：逐行读取源代码，读一行运行一行。
6. gcc: GNU Compiler Collection，当前主流C语言编译器。（gcc FILENAME.c -o EXENAME.exe       .\EXENAME.exe）如果没有"-o EXENAME.exe", 默认保存为"a.c"
7. 只有main function返回0的时候才会正常推出。在main函数里面，如果没有写return 0，就会默认返回0.
8. 返回值（return）和输出不是一个东西，程序输出（output）是hello world，返回值（return）是1

```c
#include <stdio.h>

int main(void) {
    printf("hello world\\n");
    return 1;
}
```

9. stdio.h（standard input output）.h意味着head（头文件）
10. 操作上是以byte为最小单位，即使只需要6个bit也需要填充为1个Byte（8个bit）
11. 很多机器的操作元字节是4 bytes，所以int是计算最快的。（short是两个byte聚在一块形成一个操作元字节，还需要通过解析地址来提取）

---

# Fundamental Functions

## 1. main

含义： 主函数

用法:  在操作系统运行的时候自动调用的函数，在调用其他函数的时候，如果没有在main函数之前申明，会导致程序崩溃

e.g: `int main(void){……}`——返回值总是int类型，通常return 0意味着正常运行；return 其他int代表相应的报错代号。

```c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    // 示例 1: 参数不足 (返回 1)
    if (argc < 2) {
        printf("Error: Missing arguments!\n");
        return 1; 
    }

    // 示例 2: 文件找不到 (返回 2)
    FILE *file = fopen(argv[1], "r");
    if (file == NULL) {
        printf("Error: Cannot open file %s\n", argv[1]);
        return 2;
    }

    // 示例 3: 内存分配失败 (返回 3)
    void *ptr = malloc(1000000000000); // 尝试分配巨大的内存
    if (ptr == NULL) {
        printf("Error: Out of memory!\n");
        fclose(file);
        return 3;
    }

    printf("Success!\n");
    return 0; // 只有全部成功才返回 0
}
```

e.g 在主函数之前申明自己写的函数***正确范例***：！！！注意第三行！！！

```c
#include <stdio.h>

double f(double x, double y);

int main(void)
{
    double ans = f(2, 2.5);
    printf("%lf\n", ans);
    return 0;
}

double f(double x, double y)
{
    double xy = x * y;
    return xy;
}

```

## 2. puts

含义：put string

用法：输出string并自动换行

e.g:`puts(“hello world”);`

## 3. printf

含义：print formatted:

用法：格式化打印,先写一段模版，再把空填进去。可以控制小数点位数

e.g:`printf("%s\n", "hello world");`

E.g: `printf("%.2f", 0.125);`

```c
#include <stdio.h>

int main(void) {
    printf("hello world\n");
    return 0;
}
```

## 4. Scanf

含义：scan formatted

用法：格式化输入，同样先写一段代码，在按照空填入.

e.g: `scanf(“%f\n”, &num);`

E.g: `scanf(“Age:%d\n”, &age);`——此时输入格式一定要按照“Age:20”这种格式来。

E.g:`scanf("%*s Age:%d %f", &age,&num);`输入Alex Age:20 0.1234, 会读取Alex完直接丢到不存进变量名，直接丢掉

```c
#include <stdio.h>

int main(void) {
    int a;
    int b;
    scanf("%d%d",&a,&b);
    printf("%d\n", a+b);
    return 0;
}
```

E.g: 一个超级巨大的可能令人崩溃的scanf小漏洞

```c
#include <stdio.h>

int main(void)
{
    int n;
    int sum = 0;
    scanf("%d", &n);
    while (n > 0)
    {
        int x;
        scanf("%d\n", &x);
        sum += x;
        n--;
    }
    printf("%d\n", sum);
    return 0;
} /*假设输入是2   3  4    5*/
```

！！！ line  11:  `scanf("%d\n", &a)`  v.s. `scanf("%d", &a)`:（假设对于第二种输入***2 3 4 5***） scanf formatted里面的格式如果有\n，那在读取%d之后看到“\n"，一直在等待non-whitespace然后再运行，当读到4的时候发现不是whitespace，所以继续运行，但是4 这个输入依旧在***缓冲区***里面没有被读取，直到第二个while循环，4被读取成为x_2，又碰到了"\n"，所以一定要有一个non-whitespace，which is 5，输出结果3 + 4 = 7。注意5 依然留在缓冲区里面，可能影响后续的输入！！！

## scanf / printf

| type               | format specifier |
| ------------------ | ---------------- |
| short              | %hd              |
| int                | %d               |
| long               | %ld              |
| long long          | %lld             |
| type               | format specifier |
| ---                | ---              |
| unsigned short     | %hu              |
| unsigned           | %u               |
| unsigned long      | %lu              |
| unsigned long long | %llu             |

* %f for float, %lf for double, and %Lf for long double.





# Variables(变量)

## Variable Declaration

1. C语言中的变量类型是在编译前就已经确定并且是不可改变的。（为了规范数据存储地址和数据大小）
2. 所有的变量类型都需要申明

```c
int a, b;
double x;
```

1. 写在函数内部的变量申明是局部变量(local variable)，写在 函数外的事全局变量（global variable）尽量能当局部变量就放局部变量，因为全局变量容易被污染。

```c
double x /* x 是全局变量 */
int main(void){
 int a, b; /*a, b是局部变量*/
 ......
}
```

1. 建议：在首次使用这个变量的时候申明这个变量并且进行初始化；取变量名的时候尽量保持可阅读性（带有一定的意义）。
2. Initialization（初始化）：e.g:`int a = 2, b, c = 3`;意味着a,c分别初始化为2，3，b没有初始化。

## Arithmetic types

### Integers

1. Int = 整数？——内存是有上限的，不会超过某个内存极限都能存储的最大值。

   ```c
   #include <stdio.h>
   int main(void) {
       int x = 1;
       while (1) {
    printf("%d\n", x);
    x *= 2; // x = x * 2
    getchar();
       }
   }
   ```
2. signed v.s. unsigned：n个bit代表的integer，signed取值范围是 ***[-2^(n-1), 2^(n-1)-1]*** ,unsigned范围是 ***[0, 2^(n)-1]***
3. Integer types:  ***short(= short int), int, long（= signed long = signed long int = long int）, long long***. 每个都有***signed（默认是signed, signed int 的 signed 可以被省略）*** 和***unsigned(= unsigned int)***.
4. short (16 bits only),  int (16bits - 32 bits), long (32 bits - 32 or 64 bits）, long long (64 bits only)

   ```c
   1= sizeof(char) ≤ sizeof(unsigned short) = sizeof(short) ≤ sizeof(int) ≤ sizeof(long) ≤ sizeof(long long) /*sizeof(A)意思是A包含的bytes数*/

   /*如果我要printf输出sizeof(float)，应该%什么？)*/

   printf("%d\n", (int)sizeof(1.23)) /*强制类型转换为int，因为sizeof输出肯定是整数*/
   printf("%zu\n", sizeof(1.23))
   /*实际上sizeof（T）的类型是size_t在Ubuntu 22.04上是unsigned long，windows是 unsigned long long*/
   ```

### float

1. 浮点数中的double几乎可以认为是64位的（double precision. Matches IEEE754 binary64 format if supported）
2. ***brainstorm（浮点数不是万能的）***：定义一个函数，接受两个 64 位整数，返回它们的平均值。你会使用什么返回值类型？----如果使用double（which means 64 bits as well.）let's try：

   ```c
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
   ```
3. 浮点数的误差是不可避免的，需要用两个浮点数相减小于一个容许的误差。
4. ！！！不要用浮点数代替整数运算！！！

   ```c
   /* A+B Problem */
   #include <stdio.h>

   int main(void) {
       double a, b;
       scanf("%lf%lf",&a,&b);
       printf("%lf\n", a+b);
       return 0;
   }
   ```

### Character types（本质上是int）

1. C standard 包含三种不同的字符类型：signed char，unsigned char和char, 这三个类型大小都是一个字节，signed char范围是[-127，128]，unsigned char范围是[0，256]

```c
   1 == sizeof(T) <= sizeof(short) <= sizeof(int) <= sizeof(long) <= sizeof(long
   long)
```

2. ASCII Code（American Standard Code for Information Interchange）

```c
char to_uppercase(char x){
	return x- ('a' - 'A' )
}/*This is more human-readable than:*/
char to_uppercase_magic_number(char y){
	return y - 32
}

```

3. Escape sequence
4. char使用的占位符是%c

| escape sequence | description     |
| --------------- | --------------- |
| `\'`          | single quote    |
| `\"`          | double quote    |
| `\\`          | backslash       |
| `\n`          | newline         |
| `\r`          | carriage return |
| `\t`          | horizontal tab  |

5. getchar():  return type = "int", 并且只有读取到"\n"的时候才会把输入放进缓存区，并且读取字符，可以用来清空缓存直到\n。

   1. 和scanf（" %c",……）；的区别在于可以识别EOF（End of File）e.g
   2. ```c
      #include <stdio.h>

      int main(void) {
          int c;
          printf("请输入一串字符：\n");
          while ((c = getchar()) != '\n') { // 只要还没读到换行，就一直读
              printf("字符 '%c' 对应的整数值是: %d\n", c, c);
          }
          return 0;
      }
      ```

   e.g:

```c
#include <stdio.h>

#define get_type(x) _Generic((x), \
    _Bool: "bool",                \
    char: "char",                 \
    int: "int",                   \
    float: "float",               \
    double: "double",             \
    int *: "pointer to int",      \
    default: "unknown type")

int main(void)
{
    int c;
    c = getchar();
    printf("%d\n", c);
    printf(" %s\n", get_type(c)); /*%s 是字符串的占位符。*/
    return 0;
}/*输入：2 3\n   输出是：50\nint\n,说明getchar()会返回读取到的那个字符的ASCII码，类型是int而不是char*/
```

### Bool

把整型赋值给bool的时候，只有0会返回false，其余都会是true

1. ```C
   * bool is_lowercase(char c) {
   * return (c >= 'a' && c <='z')；
     }
   ```
2. 四则运算器

   ```c
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
   ```

## Operators

### + - * /

```c
#include <stdio.h>

int main(void)
{
    double pi = 3.14;
    int d = 20;
    int c = pi * d;
    printf("%d\n", c);
}/*强制类型转换会导致精度缺失（向零取整），但是可以正常运行(base) PS D:> ./tmp.exe
62*/
```

### %

1. a % b, 其中a和b***一定***要是整型（***integer type***）

### Compound assignment operators

1. +=, -=, *=, /=
2. `a op= b`  =  `a = a = a op b `
3. signed integer overflow（不会由于overflow 而引发undefined behavior，但是会出现数值风暴）

   ```c
   int ival = 100000; longlong llval = ival;
   int result1 = ival * ival;               // (1) overflow
   long long result2 = ival * ival;         // (2) overflow when multiplication before type conversion.
   long long result3 = llval * ival;        // (3) not overflow
   long long result4 = llval * ival * ival; // (4) not overflow
   ```

### Increment and Decrement

1. a ++ and ++a increase the value of a by 1.
2. a --   and   --a decrease the value of a by 1.
3. differences between prefix and postfix

   ```c
   int x = 42;
   printf("%d\n", x++); // x becomes 43, but 42 is printed.
   int y = x++; // y is initialized with 43. x becomes 44.
   ```

### Comparison Operators

| **运算符 (Operator)** | **运算符名称 (Operator name)**  |
| --------------------------- | ------------------------------------- |
| `a == b`                  | 等于 (equal to)                       |
| `a != b`                  | 不等于 (not equal to)                 |
| `a < b`                   | 小于 (less than)                      |
| `a > b`                   | 大于 (greater than)                   |
| `a <= b`                  | 小于或等于 (less than or equal to)    |
| `a >= b`                  | 大于或等于 (greater than or equal to) |

### Logical operators

1. !   logic NOT
2. &&  logic AND
3. ||  logic OR
4. 上述先后顺序里面如果不加括号就是NOT>AND>OR
5. ?:
   1. Syntax:` condition ? expressionT : expressionF`
      1. where condition is an expression of scalar type\
   2. The ecaluation order is specified:
      1. first," condition" is evaluated
      2. if `condition `is True(compares equal Not to 0)), expressionT is evaluated, the result is the value of expressionT
      3. if `condition is False `,(compares equal to 0), expressionF
      4. ```c
             uppercase = (c >= 'a' && c <= 'z') ? c - ('a' - 'A') : c;
             printf("%c", uppercase);
         ```

# Operator Precedence

### evaluation order

1. 先乘除后加减，有括号先算括号里面。
2. ？？？f() + g() * h() is interpreted as f() + (g() * h()), but the order in which f,g and h are called is unspecified ？？？

### Associativity

1. '=' is right associated.

# Control Flow

## if - else

1. ***if (condition) {Statement}    如果没有大括号，只有condition后面第一句被认为是statement。***
2. if 和最近的else 结合抵消（在没有大括号的前提下）

## While循环

1. executes some codes repeatedly under certain condition.
2. Syntax: while (condition)  {loop_body}
3. Read an integer n, followed by n integers. Print the sum of the n integers:
4. ```c
   #include <stdio.h>

   int main(void)
   {
       int n;
       int sum = 0;
       scanf("%d", &n);
       while (n > 0)
       {
           int x;
           scanf("%d", &x);
           sum += x;
           n--;
       }
       printf("%d\n", sum);
       return 0;
   }
   ```
5. ***!!! How many times is the loop executed?  n?    n+1?!!!***
6. break statement:程序终止整个循环。
7. continue statement:程序绕过当前循环，继续进行下一轮循环。

   ```c
   #include <stdio.h>

   int main(void)
   {
       int n, sum = 0;
       scanf("%d", &n);
       while (n--) // 简写的情况下，while loop括号里面的--n和n--不一样，--n会使while循环n-1次，但是如果把判断条件写成n>0，在循环体里面写--n或者n--都是一样的！！！
       {
           int x;
           scanf("%d", &x); // If x == 42, the rest of the loop body is skipped and control goes to (*).
           if (x == 42)
           {
               // continue;
               break;
               /*ignore the input, and continue asking for a new input x.*/
           }
           sum += x;
           // (*)
       }
       printf("%d\n", sum);
   } // if 'continue': input is 3\n  1 42 3\n, output is 4\n
     // if 'break': inpuit is 3\n  1 42 3\n, output is 1\n
   ```

## For

1. Syntax: `for (init_clause; condition; iteration_expr) loop_body  `

   逻辑上等价于while，但是有一些细小的区别。

   ```c
   for (int i = 0; i < n; ++i) {
       scanf("%d", &x);
       sum += x;
   }
   printf("%d\n", sum)
   ```

* **`init_clause`（初始化子句）** **：在循环开始前执行一次。可以是表达式或变量声明（自 C99 标准起支持在内部声明）**。
* **`condition`（条件表达式）** **：在每次执行循环体*之前***进行求值 。
  * 类型可以是算术类型或指针类型 。
  * 如果结果不等于 0，则执行循环体；否则退出 。
* **`iteration_expr`（迭代表达式）** **：在每次执行完循环体****之后**求值，通常用于更新计数器 。
* **`loop_body`（循环体）** **：可以是一个单条语句，也可以是用 **`<span class="citation-40">{}</span>` 包围的代码块

### do-while

1. `do loop_body while (condition);`
2. Executes `loop_body` repeatedly until the value of `condition` compares equal to zero
3. ```c
       do
       {
           scanf("%d", &x);
           sum += x;
           i++;
           // printf("%d\n", sum);
       } while (i < n);
       printf("%d\n", sum);
   ```

### switch-case

1. First, `expression` is evaluated. Control finds the case label to which `expression `compares equal
2. Then goes to that label.Starting from the selected label, ***all subsequent statements*** are executed ***until a break***; or the end of the switch statement is reached.
3. Note that ***break;*** here has a special meaning.
4. !!! The expression in `case `must be an integer constant type(NO variables, NO floats, NO pre-input stuff.)!!!

```c
switch (op) 
{
case '+':
    printf("%lf\n", a + b); 
    break;
case '-':
    printf("%lf\n", a - b); 
    break;
case '*':
    printf("%lf\n", a * b); 
    break;
case '/':
    printf("%lf\n", a / b); 
    break;
default:
    printf("Invalid operator!\n");
    break;
}
```

```c
switch (letter){
  case'a':
  case'e':
  case'i':
  case'o':
  case'u':
    printf("%c is vowel.\n", letter);
    break;
  default:
    printf("%c is consonant.\n", letter);
}
```

# Functions

## Call and Return

1. Call: The call expression divide(x , y) takes the arguments x, y into the **divide** fuction's Parameters(a and b) `int a = x; int b = y;`
2. Return:
   1. 向调用处传递一个值（除了形参是void的函数之外）；
   2. 将控制权转交回调用处；
   3. ！！！如果在函数中没有写return，那么这个函数的返回值是undefined，如果后面调用了这个函数的返回值的话会造成undefined behavior.

```c
#include<stdlib.h>
#include<stdio.h>
double divide(int a, int b) {
  if (b == 0) {
    fprintf(stderr, "Division by zero!\n");
    exit(EXIT_FAILURE);
  }
  return 1.0 * a / b;
}

int main(void) {
  int x, y;
  scanf("%d%d", &x, &y);
  double result = divide(x, y);
  printf("%lf\n", result);
  // ...
}
```

3. The parentheses `()`  is the function call operator that* **shall NOT be omitted***
4. *Avoid unnecessary if:* 编译器很傻，总还是会认为有别的情况不通过，所以比如取绝对值你已经覆盖实数轴了还是报warning，所以最后一个else if直接写成else或者干脆在条件判断外面写最后一个情况的返回值
5. ```c
   int abs_int_1(int x) {
       if (x < 0)
           return -x; [cite: 184]
       else if (x == 0)
           return 0; [cite: 185]
       else if (x > 0)
           return x; [cite: 186]
   } // will raise warning

   int abs_int_2(int x) {
       if (x < 0)
           return -x; // 满足就直接退出了 [cite: 189]

       // 如果走到这一步，说明 x 肯定 >= 0，不需要再写 else if
       return x; [cite: 191]
   }// a more clever way with out warning
   ```

## Function declaration and definition

1. The following definitions are all the same:

   ```c
   int sum(int int);
   int sum(int a, int);
   int sum(int a, int b);
   ```
2. One function has only one definition, but there might be numerous declarations.
3. When a function is called, it must be defined.

## Scopes and name lookup

1. 当编译器在代码中遇到变量 `x` 时，它会像“剥洋葱”一样进行搜索：

1. **第一步** ：看当前的 `{ }` 代码块里有没有声明 `x`？如果有，就是它了。
2. **第二步** ：如果当前块没有，就看包裹这个块的上一层 `{ }` 里有没有 `x`？
3. **第三步** ：重复上述过程，一直推到函数的参数列表。
4. **最后一步** ：如果函数里都没有，就去函数外面的全局区域找。
5. **结果** ：如果搜遍了所有外层依然找不到，编译器就会报错：`error: 'x' undeclared`

```c
int x = 100; // 全局变量 x

int main() {
    int x = 7; // main 函数内的 x，遮蔽了全局的 x
  
    if (x == 7) {
        int x = 35; // if 块内的 x，遮蔽了 main 函数的 x
        printf("%d", x); // 这里查找 x，从 if 块开始找，直接找到 35
    }
  
    printf("%d", x); // 这里查找 x，从 main 块开始找，找到的是 7
}
```

2. As a result, declare a variable right before the use of it
3. Don't worry about the same variable name in different scopes.


# ⚠️🆘⚠️🆘

1. 在使用变量前要申明，同样，函数也一定要申明。
2. 在scanf和printf里面一定要format，先写出来格式是什么？“%d%d\n” (or so…)。
3. scanf里面变量名前要写&
4. 所有变量都需要申明类型。
5. 注意隐式类型转换.
6.
