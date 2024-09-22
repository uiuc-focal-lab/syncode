// Source: data/benchmarks/diffy_cav21_bench/nested-sa1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@
	requires N > 0;
	requires \separated(a+(0..N-1), b+(0..N-1));
*/
int main(int* a, int* b, int N)
{
	int i, j;
	int sum[1];

	/* Loop_A */  for (i = 0; i < N; i++)
	{
		a[i] = 1;
	}

	sum[0] = 0;
	/* Loop_B */  for (i = 0; i < N; i++)
	{
		/* Loop_C */  for (j = 0; j < i+1; j++)
		{
			sum[0] = sum[0] + a[j];
		}
	}

	/* Loop_D */  for (i = 0; i < N; i++)
	{
		b[i] = sum[0] + a[i];
	}

	/* Loop_E */  for (i = 0; i < N; i++)
	{
		{;
//@ assert(b[i] == N*(N+1)/2 + 1);
}

	}
}
