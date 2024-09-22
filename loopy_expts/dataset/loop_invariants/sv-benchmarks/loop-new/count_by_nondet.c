// Source: data/benchmarks/sv-benchmarks/loop-new/count_by_nondet.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define LARGE_INT 1000000
extern int unknown_int(void);

int main() {
    int i = 0;
    int k = 0;
    while(i < LARGE_INT) {
        int j = unknown_int();
        if (!(1 <= j && j < LARGE_INT)) return 0;
        i = i + j;
        k ++;
    }
    {;
//@ assert(k <= LARGE_INT);
}

    return 0;
}