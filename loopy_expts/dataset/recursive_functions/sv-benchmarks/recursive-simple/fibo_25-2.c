// Source: data/benchmarks/sv-benchmarks/recursive-simple/fibo_25-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);


/* Function_fibo */
int fibo(int n) {
    if (n < 1) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibo(n-1) + fibo(n-2);
    }
}


/* Function_main */
int main(void) {
    int x = 25;
    int result = fibo(x);
    if (result != 75025) {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
    return 0;
}