// Source: data/benchmarks/diffy_cav21_bench/standard_running-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires N > 0;
	requires \separated(a+(0..N-1), b+(0..N-1));
*/
int main(int* a, int* b, int N){
	N = unknown_int();
	int a[N];
	int b[N]; 
	int i;
	int f[1];

	/* Loop_A */  for(i = 0; i< N; i++) 
	{ 
		a[i] = unknown_int();
	}

	i = 0;
	/* Loop_B */  while ( i < N ) {
		if ( a[i] >= 0 ) b[i] = 1;
		else b[i] = 0;
		i = i + 1;
	}

	f[0] = 1;
	i = 0;
	/* Loop_C */  while ( i < N ) {
		if ( a[i] >= 0 && !b[i] ) f[0] = 0;
		if ( a[i] < 0 && b[i] ) f[0] = 0;
		i = i + 1;
	}

	{;
//@ assert( f[0] == 1 );
}
 
	return 0;
}