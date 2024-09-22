// Source: data/benchmarks/dillig/safe/12.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@
	requires size > 0;
	requires \separated(a+(0..size-1), a_copy+(0..size-1));
*/
void main(int* a, int* a_copy, int size, int k)
{	
	int i;
	/* Loop_A */  for(i=0; i<size; i++)
	{
		a_copy[i] = a[i];
	}
	
	/* Loop_B */  for(i=0; i<size; i++)
	{
		a[i] = a_copy[size-1-i];
	}
	
	if(k>=0 && k<size)
	{
		{;
//@ assert(a[k] == a_copy[size-1-k]);
}

	}

}
