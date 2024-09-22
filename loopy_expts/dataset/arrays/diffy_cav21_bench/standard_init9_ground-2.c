// Source: data/benchmarks/diffy_cav21_bench/standard_init9_ground-2.c
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
	i = 0;
	/* Loop_D */  while ( i < N ) {
		a[i] = 45;
		i = i + 1;
	}
	i = 0;
	/* Loop_E */  while ( i < N ) {
		a[i] = 46;
		i = i + 1;
	}
	i = 0;
	/* Loop_F */  while ( i < N ) {
		a[i] = 47;
		i = i + 1;
	}
	i = 0;
	/* Loop_G */  while ( i < N ) {
		a[i] = 48;
		i = i + 1;
	}
	i = 0;
	/* Loop_H */  while ( i < N ) {
		a[i] = 49;
		i = i + 1;
	}
	i = 0;
	/* Loop_I */  while ( i < N ) {
		a[i] = 50;
		i = i + 1;
	}

	int x;
	/* Loop_J */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(  a[x] == 50  );
}

	}
	return 0;
}