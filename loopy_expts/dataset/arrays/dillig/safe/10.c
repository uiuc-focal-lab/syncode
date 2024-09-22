// Source: data/benchmarks/dillig/safe/10.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@ requires size > 0;
  requires \separated(a+(0..size-1), b+(0..size-1));
  */
void main(int* a, int*b,  int size)
{
  int i;
  int j;
  /* Loop_A */  for(i=1, j=0; i<size; i+=2, j++) 
  {
	a[j] = b[i];
  }

  /* Loop_B */  for(i=1, j=0; i<size; i+=2, j++)
  {
	{;
//@ assert(a[j] == b[2*j+1]);
}

  }
}