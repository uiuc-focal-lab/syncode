// Source: data/benchmarks/diffy_cav21_bench/nested-nli3.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int N;

int main()
{
	N = unknown_int();
	if(N <= 0) return 1;
	assume(N <= 2147483647/sizeof(int));

	int i, j;
	int a[N];

	/* Loop_A */  for (i = 0; i < N; i++)
	{
		a[i] = 0;
	}

	/* Loop_B */  for (i = 0; i < N; i++)
	{
		/* Loop_C */  for (j = 0; j < N; j++)
		{
			a[i] = a[i] + i;
		}
	}

	/* Loop_D */  for (i = 0; i < N; i++)
	{
		{;
//@ assert(a[i] == N*i);
}

	}
}
