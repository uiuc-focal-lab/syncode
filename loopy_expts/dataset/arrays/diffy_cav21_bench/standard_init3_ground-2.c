// Source: data/benchmarks/diffy_cav21_bench/standard_init3_ground-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int N;
int main ( ) {
	N = unknown_int();
	if (N <= 0) return 1;
	int a[N];
	int i = 0;
	/* Loop_A */  while ( i < N ) {
		a[i] = 42;
		i = i + 1;
	}
	i = 0;
	/* Loop_B */  while ( i < N ) {
		a[i] = 43;
		i = i + 1;
	}
	i = 0;
	/* Loop_C */  while ( i < N ) {
		a[i] = 44;
		i = i + 1;
	}

	int x;
	/* Loop_D */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(  a[x] == 44  );
}

	}
	return 0;
}