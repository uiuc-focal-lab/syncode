// Source: data/benchmarks/diffy_cav21_bench/cond2s2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int N;

int main()
{
	N = unknown_int();
	if(N <= 0) return 1;

	int i;
	int sum1[1];
	int sum2[1];
	int c[N];

	sum1[0] = N;
	/* Loop_A */  for(i=0; i<N; i++)
	{
		sum1[0] = sum1[0] + 1;
	}

	sum2[0] = 0;
	/* Loop_B */  for(i=0; i<N; i++)
	{
		sum2[0] = sum2[0] + 2;
	}

	/* Loop_C */  for(i=0; i<N; i++)
	{
		if(i != 0 && N % i == 0)
		{
			c[i] = sum1[0];
		} else {
			c[i] = sum2[0]; 
		}
	}

	/* Loop_D */  for(i=0; i<N; i++)
	{
		{;
//@ assert(c[i] == 2*N);
}
 
	}
	return 1;
}