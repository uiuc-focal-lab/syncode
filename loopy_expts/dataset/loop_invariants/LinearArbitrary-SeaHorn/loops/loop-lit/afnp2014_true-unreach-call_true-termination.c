// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loop-lit/afnp2014_true-unreach-call_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int x = 1;
    int y = 0;
    while (y < 1000 && unknown_int()) {
        x = x + y;
        y = y + 1;
    }
    {;
//@ assert(x >= y);
}

    return 0;
}