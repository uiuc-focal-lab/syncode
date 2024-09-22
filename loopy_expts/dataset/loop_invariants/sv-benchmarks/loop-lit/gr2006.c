// Source: data/benchmarks/sv-benchmarks/loop-lit/gr2006.c
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