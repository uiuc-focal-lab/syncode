// Source: data/benchmarks/diffy_cav21_bench/nsqm.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@
	requires N > 0;
	requires \separated(a+(0..N-1), b+(0..N-1));
*/
int main(int* a, int* b, int N)
{
	int i;

	b[0] = 1;
	a[0] = N+1;

	/* Loop_A */  for(i=1; i<N; i++)
	{
		b[i] = b[i-1] + 2;
	}

	/* Loop_B */  for(i=1; i<N; i++)
	{
		a[i] = a[i-1] + b[i-1] + 2;
	}

	/* Loop_C */  for(i=0; i<N; i++)
	{
		{;
//@ assert(a[i] == N + (i+1)*(i+1));
}

	}
	return 1;
}