// Source: data/benchmarks/diffy_cav21_bench/standard_copy2_ground-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires N > 0;
	requires \separated(a1+(0..N-1), a2+(0..N-1), a3+(0..N-1));
*/
int main(int* a1, int* a2, int* a3, int N ) {
	int a;
	/* Loop_A */  for ( a = 0 ; a < N ; a++ ) {
		a1[a] = unknown_int();
	}

	int i;
	/* Loop_B */  for ( i = 0 ; i < N ; i++ ) {
		a2[i] = a1[i];
	}
	/* Loop_C */  for ( i = 0 ; i < N ; i++ ) {
		a3[i] = a2[i];
	}

	int x;
	/* Loop_D */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(  a1[x] == a3[x]  );
}

	}
	return 0;
}
