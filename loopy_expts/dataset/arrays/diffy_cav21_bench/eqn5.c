// Source: data/benchmarks/diffy_cav21_bench/eqn5.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@
	requires N > 0;
	requires \separated(a+(0..N-1), b+(0..N-1));
*/
int main(int* a, int* b, int N)
{

	int i;

	a[0] = 10;
	b[0] = 1;
	/* Loop_A */  for(i=1; i<N; i++)
	{
		a[i] = a[i-1] + 10;
	}

	/* Loop_B */  for(i=1; i<N; i++)
	{
		b[i] = b[i-1] + a[i-1];
	}

	/* Loop_C */  for(i=0; i<N; i++)
	{
		{;
//@ assert(b[i] == 5*i*i + 5*i + 1);
}

	}
	return 1;
}