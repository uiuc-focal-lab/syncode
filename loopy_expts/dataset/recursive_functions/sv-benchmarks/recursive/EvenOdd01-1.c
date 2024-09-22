// Source: data/benchmarks/sv-benchmarks/recursive/EvenOdd01-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);

int isOdd(int n);
int isEven(int n);


/* Function_isOdd */
int isOdd(int n) {
    if (n == 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return isEven(n - 1);
    }
}


/* Function_isEven */
int isEven(int n) {
    if (n == 0) {
        return 1;
    } else if (n == 1) {
        return 0;
    } else {
        return isOdd(n - 1);
    }
}


/* Function_main */
int main() {
    int n = unknown_int();
    if (n < 0) {
        return 0;
    }
    int result = isOdd(n);
    int mod = n % 2;
    if (result < 0 || result == mod) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}