// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loop-lit/gr2006_true-unreach-call_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
    int x,y;
    x = 0;
    y = 0;
    while (1) {
        if (x < 50) {
            y++;
        } else {
            y--;
        }
        if (y < 0) break;
        x++;
    }
    {;
//@ assert(x == 100);
}

    return 0;
}