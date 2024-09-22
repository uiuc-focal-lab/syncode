// Source: data/benchmarks/diffy_cav21_bench/nested-unb3.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@
	requires N > 0;
	requires \separated(a+(0..N-1), b+(0..N-1));
*/
int main(int* a, int* b, int N)
{
	int i, j;

	/* Loop_A */  for (i = 0; i < N; i++)
	{
		b[i] = 1;
	}

	/* Loop_B */  for (i = 0; i < N; i++)
	{
		/* Loop_C */  for (j = 0; j < N; j++)
		{
			b[j] = b[j] + a[j];
		}
	}

	/* Loop_D */  for (i = 0; i < N; i++)
	{
		{;
//@ assert(b[i] == (N * a[i]) + 1);
}

	}
}
