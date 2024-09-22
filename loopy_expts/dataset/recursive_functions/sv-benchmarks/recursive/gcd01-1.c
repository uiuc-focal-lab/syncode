// Source: data/benchmarks/sv-benchmarks/recursive/gcd01-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_gcd */
int gcd(int y1, int y2) {
    if (y1 <= 0 || y2 <= 0) {
        return 0;
    }
    if (y1 == y2) {
        return y1;
    }
    if (y1 > y2) {
        return gcd(y1 - y2, y2);
    }
    return gcd(y1, y2 - y1);
}


/* Function_main */
int main() {
    int m = unknown_int();
    if (m <= 0 || m > 2147483647) {
        return 0;
    }
    int n = unknown_int();
    if (n <= 0 || n > 2147483647) {
        return 0;
    }
    int z = gcd(m, n);
    if (z < 1 && m > 0 && n > 0) {
        { ERROR: {; 
//@ assert(\false);
}
}
    } else {
        return 0;
    }
}