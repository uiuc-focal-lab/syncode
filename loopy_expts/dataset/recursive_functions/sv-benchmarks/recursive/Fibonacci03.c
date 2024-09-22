// Source: data/benchmarks/sv-benchmarks/recursive/Fibonacci03.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_fibonacci */
int fibonacci(int n) {
    if (n < 1) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibonacci(n-1) + fibonacci(n-2);
    }
}


/* Function_main */
int main() {
    int x = unknown_int();
    if (x > 46) {
        return 0;
    }
    int result = fibonacci(x);
    if (x < 9 || result >= 34) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}
    