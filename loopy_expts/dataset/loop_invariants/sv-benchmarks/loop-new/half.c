// Source: data/benchmarks/sv-benchmarks/loop-new/half.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define LARGE_INT 1000000
extern int unknown_int(void);

int main() {
    int i = 0;
    int n = 0;
    int k = unknown_int();
    if (!(k <= LARGE_INT && k >= -LARGE_INT)) return 0;
    for(i = 0; i < 2*k; i++) {
        if (i % 2 == 0) {
            n ++;
        }
    }
    {;
//@ assert(k < 0 || n == k);
}

    return 0;
}