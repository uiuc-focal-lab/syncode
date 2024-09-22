// Source: data/benchmarks/sv-benchmarks/loop-new/gauss_sum.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int n, sum, i;
    n = unknown_int();
    if (!(1 <= n && n <= 1000)) return 0;
    sum = 0;
    for(i = 1; i <= n; i++) {
        sum = sum + i;
    }
    {;
//@ assert(2*sum == n*(n+1));
}

    return 0;
}