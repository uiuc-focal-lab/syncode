// Source: data/benchmarks/diffy_cav21_bench/standard_compareModified_ground.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires SIZE > 0;
	requires \separated(a+(0..SIZE-1), b+(0..SIZE-1), c+(0..SIZE-1));
*/
int main(int* a, int* b, int* c, int SIZE)
{
	int i = 0;
	int rv[1];

	rv[0] = 1;
	/* Loop_A */  for (int j = 0; j < SIZE ; j++ ) {
		a[j] = unknown_int();
		b[j] = unknown_int();
	}

	/* Loop_B */  while ( i < SIZE ) {
		if ( a[i] != b[i] ) {
			rv[0] = 0;
		}
		c[i] = a[i];
		i = i+1;
	}

	int x;

	/* Loop_C */  for ( x = 0 ; x < SIZE ; x++ ) {
		{;
//@ assert(  a[x] == c[x]  );
}

	}
	return 0;
}