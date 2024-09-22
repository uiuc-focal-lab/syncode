// Source: data/benchmarks/dillig/safe/1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

//@ requires size > 0;
void main(int* a, int c, int size)
{
  int i;
  /* Loop_A */  for(i=0; i<size; i++) 
  {
	a[i] = c;
  }

  /* Loop_B */  for(i=0; i<size; i++)
  {
	{;
//@ assert(a[i] == c);
}

  }
}
