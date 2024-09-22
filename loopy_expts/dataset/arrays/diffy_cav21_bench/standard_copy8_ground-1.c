// Source: data/benchmarks/diffy_cav21_bench/standard_copy8_ground-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires N > 0;
	requires \separated(a1+(0..N-1), a2+(0..N-1), a3+(0..N-1), a4+(0..N-1), a5+(0..N-1), a6+(0..N-1), a7+(0..N-1), a8+(0..N-1), a9+(0..N-1));
*/
int main(int* a1, int* a2, int* a3, int* a4, int* a5, int* a6, int* a7, int* a8, int* a9, int N) {

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
	/* Loop_H */  for ( i = 0 ; i < N ; i++ ) {
		a8[i] = a7[i];
	}
	/* Loop_I */  for ( i = 0 ; i < N ; i++ ) {
		a9[i] = a8[i];
	}

	int x;
	/* Loop_J */  for ( x = 0 ; x < N ; x++ ) {
		{;
//@ assert(  a1[x] == a9[x]  );
}

	}
	return 0;
}
