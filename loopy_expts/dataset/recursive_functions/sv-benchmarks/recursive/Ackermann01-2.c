// Source: data/benchmarks/sv-benchmarks/recursive/Ackermann01-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_ackermann */
int ackermann(int m, int n) {
    if (m==0) {
        return n+1;
    }
    if (n==0) {
        return ackermann(m-1,1);
    }
    return ackermann(m-1,ackermann(m,n-1));
}


/* Function_main */
int main() {
    int m = unknown_int();
    if (m < 0 || m > 3) {
        
        return 0;
    }
    int n = unknown_int();
    if (n < 0 || n > 23) {
        
        return 0;
    }
    int result = ackermann(m,n);
    if (m < 0 || n < 0 || result >= 0) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}