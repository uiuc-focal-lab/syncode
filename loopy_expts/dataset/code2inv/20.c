// Source: data/benchmarks/code2inv/20.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main()
{
    int z1,z2,z3;
    int x = 0;
    int m = 0;
    int n;

    while (x < n) {
        if (unknown()) {
            m = x;
        }
        x = x + 1;
    }

    if(n > 0) {
       
       {;
//@ assert(m >= 0);
}

    }
}