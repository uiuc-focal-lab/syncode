// Source: data/benchmarks/diffy_cav21_bench/ms4.c
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

	/* Loop_A */  for(i=0; i<N; i++)
	{
		a[i] = i%4;
	}

	/* Loop_B */  for(i=0; i<N; i++)
	{
		if(i==0) {
			sum[0] = 0;
		} else {
			sum[0] = sum[0] + a[i];
		}
	}
	{;
//@ assert(sum[0] <= 3*N);
}

	return 1;
}