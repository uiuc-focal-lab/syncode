// Source: data/benchmarks/LinearArbitrary-SeaHorn/llreve/barthe2_merged_safe.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

void main() {
	int n = unknown();
    int x1 = 0;
    int x2 = 0;

    int i1 = 0; 
    int i2 = 1; 
	while (1)
	{
    	if ( i1 <= n) {
	        x1 = x1 + i1;
    	    i1++;
	    }

		if ( i2 <= n) {
	        x2 = x2 + i2;
    	    i2++;
		}

		if (i1>n && i2>n) break;
		{;
//@ assert(x2==x1+i1);
}

    }
}