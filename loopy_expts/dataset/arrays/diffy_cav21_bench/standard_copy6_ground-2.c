// Source: data/benchmarks/diffy_cav21_bench/standard_copy6_ground-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires N > 0;
	requires \separated(a1+(0..N-1), a2+(0..N-1), a3+(0..N-1), a4+(0..N-1), a5+(0..N-1), a6+(0..N-1), a7+(0..N-1));
*/
int main(int* a1, int* a2, int* a3, int* a4, int* a5, int* a6, int* a7, int N) {

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
	/* Loop_D */  for ( i = 0 ; i < N ; i++ ) {
		a4[i] = a3[i];
	}
	/* Loop_E */  for ( i = 0 ; i < N ; i++ ) {
		a5[i] = a4[i];
	}
	/* Loop_F */  for ( i = 0 ; i < N ; i++ ) {
		a6[i] = a5[i];
	}
	/* Loop_G */  for ( i = 0 ; i < N ; i++ ) {
		a7[i] = a6[i];
	}

	int x;
	/* Loop_H */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(  a1[x] == a7[x]  );
}

	}
	return 0;
}
