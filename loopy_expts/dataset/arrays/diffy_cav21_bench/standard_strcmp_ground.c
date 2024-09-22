// Source: data/benchmarks/diffy_cav21_bench/standard_strcmp_ground.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires N > 0;
	requires \separated(a+(0..N-1), b+(0..N-1));
*/
int main(int* a, int* b, int N){
	int i; 
	int c[1];

	/* Loop_A */  for(i = 0; i < N; i++) 
	{
		a[i] = unknown_int();
		b[i] = unknown_int();
	}

	c[0] = 0;
	i = 0;
	/* Loop_B */  while ( i < N ) {
		if( a[i] != b[i] ) c[0] = 1;
		i = i + 1;
	}

	int x;
	/* Loop_C */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(c[0] == 1 ||  a[x] == b[x]  );
}

	}
	return 0;
}