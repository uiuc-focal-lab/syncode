// Source: data/benchmarks/diffy_cav21_bench/standard_maxInArray_ground.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int N;

int main( ) {
	N = unknown_int();
	if ( N <= 0 ) return 1;
	
	int a[N];
	int max[1];

	max[0] = 0;
	/* Loop_A */  for (int j = 0; j < N ; j++ ) {
		a[j] = unknown_int();
	}

	int i = 0;
	/* Loop_B */  while ( i < N ) {
		if ( a[i] > max[0] ) {
			max[0] = a[i];
		}
		i = i + 1;
	}

	int x;
	/* Loop_C */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(  a[x] <= max[0] );
}

	}
	return 0;
}