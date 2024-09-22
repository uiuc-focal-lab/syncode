// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loop-lit/jm2006_true-unreach-call_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int i, j;
    i = unknown_int();
    j = unknown_int();
    if (!(i >= 0 && j >= 0)) return 0;
    int x = i;
    int y = j;
    while(x != 0) {
        x--;
        y--;
    }

    if (i == j) {
        {;
//@ assert(y == 0);
}

    }
    return 0;
}