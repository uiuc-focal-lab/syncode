// Source: data/benchmarks/diffy_cav21_bench/s5if.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int N;

int main()
{
	N = unknown_int();
	if(N <= 0) return 1;

	int i;
	int sum[1];
	int a[N];

	sum[0] = 0;
	/* Loop_A */  for(i=0; i<N; i++)
	{
		a[i] = 5;
	}

	/* Loop_B */  for(i=0; i<N; i++)
	{
		if(a[i] == 5) {
			sum[0] = sum[0] + a[i];
		} else {
			sum[0] = sum[0] * a[i];
		}
	}

	{;
//@ assert(sum[0] == 5*N);
}

	return 1;
}