// Source: data/benchmarks/dillig/safe/21.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void main(int* a, int size, int elem)
{
	int i;
	int pos = -1;
	/* Loop_A */  for(i=0; i<size; i++)
	{
		if(a[i] == elem) 
		{
			pos = i;
			break;
		}
	}
	if(pos!= -1) {;
//@ assert(a[pos] == elem);
}
	
}
