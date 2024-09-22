// Source: data/benchmarks/sv-benchmarks/recursive-simple/fibo_2calls_25-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);

int fibo1(int n);
int fibo2(int n);


/* Function_fibo1 */
int fibo1(int n) {
    if (n < 1) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibo2(n-1) + fibo2(n-2);
    }
}


/* Function_fibo2 */
int fibo2(int n) {
    if (n < 1) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibo1(n-1) + fibo1(n-2);
    }
}


/* Function_main */
int main(void) {
    int x = 25;
    int result = fibo1(x);
    if (result != 75025) {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
    return 0;
}