// Source: data/benchmarks/sv-benchmarks/recursive/Fibonacci02.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);


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
    int x = 9;
    int result = fibonacci(x);
    if (result == 34) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}