// Source: data/benchmarks/sv-benchmarks/recursive/Primes.c
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
    if (m == 1) {
        return 1;
    }
    return n + mult(n, m - 1);
}


/* Function_multiple_of */
int multiple_of(int n, int m) {
    if (m < 0) {
        return multiple_of(n, -m);
    }
    if (n < 0) {
        return multiple_of(-n, m); 
    }
    if (m == 0) {
        return 0; 
    }
    if (n == 0) {
        return 1; 
    }
    return multiple_of(n - m, m);
}

int is_prime_(int n, int m);
int is_prime(int n);


/* Function_is_prime */
int is_prime(int n) {
    return is_prime_(n, n - 1);
}


/* Function_is_prime_ */
int is_prime_(int n, int m) {
    if (n <= 1) {
        return 0; 
    }
    if (n == 2) {
        return 1; 
    }
    if (n > 2) {
        if (m <= 1) {
            return 1; 
        } else {
            if (multiple_of(n, m) == 0) {
                return 0; 
            }
            return is_prime_(n, m - 1);
        }
    }
}


/* Function_main */
int main() {
    int n = unknown_int();
    if (n < 1 || n > 46340) {
        
        return 0;
    }
    int result = is_prime(n);
    int f1 = unknown_int();
    if (f1 < 1 || f1 > 46340) {
        
        return 0;
    }
    int f2 = unknown_int();
    if (f2 < 1 || f2 > 46340) {
        
        return 0;
    }

    if (result == 1 && mult(f1, f2) == n && f1 > 1 && f2 > 1) {
        { ERROR: {; 
//@ assert(\false);
}
}
    } else {
        return 0;
    }
}