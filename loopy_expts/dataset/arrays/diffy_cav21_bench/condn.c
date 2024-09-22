// Source: data/benchmarks/diffy_cav21_bench/condn.c
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

	/* Loop_A */  for(i=0; i<N; i++)
	{
		a[i] = unknown_int();
	}

	/* Loop_B */  for(i=0; i<N; i++)
	{
		if(a[i] < N) {
			a[i] = a[i];
		} else {
			a[i] = N;
		}
	}

	/* Loop_C */  for(i=0; i<N; i++)
	{
		{;
//@ assert(a[i] <= N);
}

	}
	return 1;
}