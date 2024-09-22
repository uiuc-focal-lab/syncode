// Source: data/benchmarks/diffy_cav21_bench/pcomp.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@
	requires N > 0;
	requires \separated(a+(0..N-1), b+(0..N-1), c+(0..N-1));
*/
int main(int* a, int* b, int* c, int N)
{
	int i;

	a[0] = 6;
	b[0] = 1;
	c[0] = 0;

	/* Loop_A */  for(i=1; i<N; i++)
	{
		a[i] = a[i-1] + 6;
	}

	/* Loop_B */  for(i=1; i<N; i++)
	{
		b[i] = b[i-1] + a[i-1];
	}

	/* Loop_C */  for(i=1; i<N; i++)
	{
		c[i] = c[i-1] + b[i-1];
	}

	/* Loop_D */  for(i=0; i<N; i++)
	{
		{;
//@ assert(c[i] == i*i*i);
}

	}
	return 1;
}