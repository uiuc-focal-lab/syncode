// Source: data/benchmarks/sv-benchmarks/recursive/MultCommutative-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_mult */
int mult(int n, int m) {
    if (m < 0) {
        return mult(n, -m);
    }
    if (m == 0) {
        return 0;
    }
    return n + mult(n, m - 1);
}


/* Function_main */
int main() {
    int m = unknown_int();
    if (m < 0 || m > 46340) {
        return 0;
    }
    int n = unknown_int();
    if (n < 0 || n > 46340) {
        return 0;
    }
    int res1 = mult(m, n);
    int res2 = mult(n, m);
    if (res1 != res2 && m > 0 && n > 0) {
        { ERROR: {; 
//@ assert(\false);
}
}
    } else {
        return 0;
    }
}