// Source: data/benchmarks/sv-benchmarks/recursive/Addition03-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_addition */
long long addition(long long m, long long n) {
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
    int n = unknown_int();
    long long result = addition(m,n);
    if (m < 100 || n < 100 || result >= 200) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}