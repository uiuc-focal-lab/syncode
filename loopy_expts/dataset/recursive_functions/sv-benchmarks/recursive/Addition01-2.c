// Source: data/benchmarks/sv-benchmarks/recursive/Addition01-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_addition */
int addition(int m, int n) {
    if (n == 0) {
        return m;
    }
    if (n > 0) {
        return addition(m+1, n-1);
    }
    if (n < 0) {
        return addition(m-1, n+1);
    }
}


/* Function_main */
int main() {
    int m = unknown_int();
    if (m < 0 || m > 1073741823) {
        
        return 0;
    }
    int n = unknown_int();
    if (n < 0 || n > 1073741823) {
        
        return 0;
    }
    int result = addition(m,n);
    if (result == m + n) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}