// Source: data/benchmarks/LinearArbitrary-SeaHorn/llreve/barthe_merged_safe.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int __mark(int);
void main() {
	int n, c;
    n = unknown();
    c = unknown();
    int i = 0;
    int j1 = 0;
    int x1 = 0;
    int j2 = c;
    int x2 = 0;

    while ( (i < n)) {
        
        j1 = 5 * i + c;
		{;
//@ assert(j1 == j2);
}

        x1 = x1 + j1;
        x2 = x2 + j2;
		{;
//@ assert(x1 == x2);
}

        j2 = j2 + 5;
        i++;
    }
}