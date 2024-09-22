// Source: data/benchmarks/sv-benchmarks/loop-lit/css2003.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define LARGE_INT 1000000
extern int unknown_int(void);

int main() {
    int i,j,k;
    i = 1;
    j = 1;
    k = unknown_int();
    if (!(0 <= k && k <= 1)) return 0;
    while (i < LARGE_INT) {
	i = i + 1;
	j = j + k;
	k = k - 1;
	{;
//@ assert(1 <= i + k && i + k <= 2 && i >= 1);
}

    }
    return 0;
}