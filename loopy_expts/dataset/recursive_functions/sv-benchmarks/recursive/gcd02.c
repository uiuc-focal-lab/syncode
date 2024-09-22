// Source: data/benchmarks/sv-benchmarks/recursive/gcd02.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_gcd */
int gcd(int y1, int y2) {
    if (y1 <= 0 || y2 <= 0) {
        
        { ERROR: {; 
//@ assert(\false);
}
}
    }
    if (y1 == y2) {
        return y1;
    }
    if (y1 > y2) {
        return gcd(y1 - y2, y2);
    }
    return gcd(y1, y2 - y1);
}


/* Function_divides */
int divides(int n, int m) {
    if (m == 0) {
        return 1; 
    }
    if (n > m) {
        return 0; 
    }
    return divides(n, m - n);
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
    if (m > 0 && n > 0) {
        int z = gcd(m, n);
        if (divides(z, m) == 0) {
            { ERROR: {; 
//@ assert(\false);
}
}
        } else {
            return 0;
        }
    }
}