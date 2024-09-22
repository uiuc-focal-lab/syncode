// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loop-lit/jm2006_variant_true-unreach-call_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define LARGE_INT 1000000
extern int unknown_int(void);

int main() {
    int i, j;
    i = unknown_int();
    j = unknown_int();

    if (!(i >= 0 && i <= LARGE_INT)) return 0;
    if (!(j >= 0)) return 0;
    int x = i;
    int y = j;
    int z = 0;
    while(x != 0) {
        x --;
        y -= 2;
        z ++;
    }
    if (i == j) {
        {;
//@ assert(y == -z);
}

    }
    return 0;
}