// Source: data/benchmarks/sv-benchmarks/loop-lit/bhmr2007.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define LARGE_INT 1000000
extern int unknown_int(void);

int main() {
    int i, n, a, b;
    i = 0; a = 0; b = 0; n = unknown_int();
    if (!(n >= 0 && n <= LARGE_INT)) return 0;
    while (i < n) {
        if (unknown_int()) {
            a = a + 1;
            b = b + 2;
        } else {
            a = a + 2;
            b = b + 1;
        }
        i = i + 1;
    }
    {;
//@ assert(a + b == 3*n);
}

    return 0;
}