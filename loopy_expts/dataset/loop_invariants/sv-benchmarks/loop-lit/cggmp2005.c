// Source: data/benchmarks/sv-benchmarks/loop-lit/cggmp2005.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
    int i,j;
    i = 1;
    j = 10;
    while (j >= i) {
        i = i + 2;
        j = -1 + j;
    }
    {;
//@ assert(j == 6);
}

    return 0;
}