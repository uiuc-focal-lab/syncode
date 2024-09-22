// Source: data/benchmarks/diffy_cav21_bench/standard_minInArray_ground-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int N;

int main( ) {
	N = unknown_int();
	if (N <= 0) return 1;
	int i;
	int a[N];
	int min[1];

	min[0]=0;
	/* Loop_A */  for(i = 0; i < N; i++)
	{
		a[i] = unknown_int();
	}

	i = 0;
	/* Loop_B */  while ( i < N ) {
		if ( a[i] < min[0] ) {
			min[0] = a[i];
		}
		i = i + 1;
	}

	int x;
	/* Loop_C */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(  a[x] >= min[0]  );
}

	}
	return 0;
}