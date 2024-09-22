// Source: data/benchmarks/diffy_cav21_bench/zero_sum4.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int SIZE;

int main()
{
	SIZE = unknown_int();
	if(SIZE <= 0) return 1;

	int i;
	int a[SIZE];
	int sum[1];

	sum[0]=0;
	/* Loop_A */  for(i = 0; i < SIZE; i++) 
	{
		a[i] = unknown_int();
	}

	/* Loop_B */  for(i = 0; i < SIZE; i++)
	{
		sum[0] = sum[0] + a[i];
	}

	/* Loop_C */  for(i = 0; i < SIZE; i++)
	{
		sum[0] = sum[0] - a[i];
	}

	/* Loop_D */  for(i = 0; i < SIZE; i++)
	{
		sum[0] = sum[0] + a[i];
	}

	/* Loop_E */  for(i = 0; i < SIZE; i++)
	{
		sum[0] = sum[0] - a[i];
	}

	/* Loop_F */  for(i = 0; i < SIZE; i++)
	{
		sum[0] = sum[0] + a[i];
	}

	/* Loop_G */  for(i = 0; i < SIZE; i++)
	{
		sum[0] = sum[0] - a[i];
	}

	/* Loop_H */  for(i = 0; i < SIZE; i++)
	{
		sum[0] = sum[0] + a[i];
	}

	/* Loop_I */  for(i = 0; i < SIZE; i++)
	{
		sum[0] = sum[0] - a[i];
	}

	{;
//@ assert(sum[0] == 0);
}

	return 1;
}