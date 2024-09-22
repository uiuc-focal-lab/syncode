// Source: data/benchmarks/dillig/safe/5.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

//@ requires size > 0;
void main(int* a,  int size)
{
  int i;
  /* Loop_A */  for(i=0; i<size; i+=2) 
  {
	a[i] = 1;
  }

  /* Loop_B */  for(i=0; i<size; i+=2)
  {
	{;
//@ assert(a[i] == 1);
}

  }
}
