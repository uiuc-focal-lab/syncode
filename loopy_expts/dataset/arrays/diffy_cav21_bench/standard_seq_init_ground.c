// Source: data/benchmarks/diffy_cav21_bench/standard_seq_init_ground.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int SIZE;
int main( ) {
	SIZE = unknown_int();
	int a[SIZE];
	int i;

	a[0] = 7;
	i = 1;
	/* Loop_A */  while( i < SIZE ) {
		a[i] = a[i-1] + 1;
		i = i + 1;
	}

	int x;
	/* Loop_B */  for ( x = 1 ; x < SIZE ; x++ ) {
		{;
//@ assert(  a[x] >= a[x-1]  );
}

	}
	return 0;
}