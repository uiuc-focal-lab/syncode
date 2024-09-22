// Source: data/benchmarks/dillig/safe/22.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void main(int* a, int size)
{
	int pos = -1;
	int i;
	/* Loop_A */  for(i=0; i<size; i++)
	{
		if(a[i] != 0) {
			pos = i;
			break;
		}
	}
	
	if(pos !=-1) {;
//@ assert(a[i] !=0);
}

}
