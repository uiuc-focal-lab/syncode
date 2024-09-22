// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loop-new/count_by_1_true-unreach-call_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define LARGE_INT 1000000

int main() {
    int i;
    for (i = 0; i < LARGE_INT; i++) ;
    {;
//@ assert(i == LARGE_INT);
}

    return 0;
}