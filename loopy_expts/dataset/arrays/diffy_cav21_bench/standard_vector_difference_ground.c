// Source: data/benchmarks/diffy_cav21_bench/standard_vector_difference_ground.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires SIZE > 0;
	requires \separated(a+(0..SIZE-1), b+(0..SIZE-1), c+(0..SIZE-1));
*/
int main(int* a, int* b, int* c, int SIZE){
	int i = 0;

	/* Loop_A */  for(i = 0; i < SIZE; i++)
	{
		a[i] = unknown_int();
		b[i] = unknown_int();
	}

	i = 0;
	/* Loop_B */  while (i < SIZE) {
		c[i] = a[i] - b[i];
		i = i + 1;
	}

	int x;
	/* Loop_C */  for (x = 0; x < SIZE; x++) {
		{;
//@ assert(c[x] == a[x] - b[x]);
}

	}

	return 0;
}
