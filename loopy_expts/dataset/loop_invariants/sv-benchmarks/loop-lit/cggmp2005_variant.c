// Source: data/benchmarks/sv-benchmarks/loop-lit/cggmp2005_variant.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define LARGE_INT 1000000
extern int unknown_int(void);

int main() {
    int lo, mid, hi;
    lo = 0;
    mid = unknown_int();
    if (!(mid > 0 && mid <= LARGE_INT)) return 0;
    hi = 2*mid;
    
    while (mid > 0) {
        lo = lo + 1;
        hi = hi - 1;
        mid = mid - 1;
    }
    {;
//@ assert(lo == hi);
}

    return 0;
}