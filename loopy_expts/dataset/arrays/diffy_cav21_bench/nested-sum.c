// Source: data/benchmarks/diffy_cav21_bench/nested-sum.c
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
	int sum[1];

	sum[0] = 0;
	/* Loop_A */  for (i = 0; i < N; i++)
	{
		/* Loop_B */  for (j = 0; j < i+1; j++)
		{
			sum[0] = sum[0] + 1;
		}
	}

	{;
//@ assert(sum[0] == N*(N+1)/2);
}

}
