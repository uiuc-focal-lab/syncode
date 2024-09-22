// Source: data/benchmarks/diffy_cav21_bench/standard_copy1_ground-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires N > 0;
	requires \separated(a1+(0..N-1), a2+(0..N-1));
*/
int main(int* a1, int* a2, int N) {
	int a;
	/* Loop_A */  for ( a = 0 ; a < N ; a++ ) {
		a1[a] = unknown_int();
	}

	int i;
	/* Loop_B */  for ( i = 0 ; i < N ; i++ ) {
		a2[i] = a1[i];
	}

	int x;
	/* Loop_C */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(  a1[x] == a2[x]  );
}

	}
	return 0;
}
