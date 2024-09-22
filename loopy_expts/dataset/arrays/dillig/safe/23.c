// Source: data/benchmarks/dillig/safe/23.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@
	requires size_a > 0 && size_b > 0;
	requires \separated(a+(0..size_a+size_b-1), b+(0..size_a-1));
*/
void main(int* a,  int size_a, int* b, int size_b, int k)
{
	int i = size_a;
	/* Loop_A */  for(; i < size_a+size_b; i++)
	{
		a[i] = b[i-size_a];
	}
	if(k >=size_a && k < size_a+size_b)
		{;
//@ assert(a[k] == b[k-size_a]);
}

}
