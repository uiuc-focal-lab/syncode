// Source: data/benchmarks/diffy_cav21_bench/condi.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int N;

int main()
{
	N = unknown_int();
	if(N <= 0) return 1;

	int i;
	int a[N];

	/* Loop_A */  for (i = 0; i < N; i++)
	{
		a[i] = 3;
	}

	/* Loop_B */  for (i = 0; i < N; i++)
	{
		if(N % (i + 1) == 0)
		{
			a[i] = a[i] - 1;
		} else {
			a[i] = a[i] - 2;
		}
	}

	/* Loop_C */  for (i = 0; i < N; i++)
	{
		{;
//@ assert(a[i] <= 2);
}

	}
	return 1;
}