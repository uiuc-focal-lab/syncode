// Source: data/benchmarks/diffy_cav21_bench/indp2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int N;

int main()
{
	N = unknown_int();
	if(N <=0 ) return 1;

	int i;
	int a[N];

	/* Loop_A */  for(i=0;i<N;i++)
	{
		a[i]=((i-1)*(i+1));
	}

	/* Loop_B */  for(i=0;i<N;i++)
	{
		a[i]=a[i]-(i*i);
	}

	/* Loop_C */  for(i=0;i<N;i++)
	{
		a[i]=a[i]+1;
	}

	/* Loop_D */  for(i=0;i<N;i++)
	{
		{;
//@ assert(a[i]==0);
}

	}

	return 1;
}