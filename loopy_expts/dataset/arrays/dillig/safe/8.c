// Source: data/benchmarks/dillig/safe/8.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@ requires size > 0;
 requires \separated(a+(0..size-1), b+(0..size-1));
 */
void main(int* a, int*b,  int size)
{
  int i;
  /* Loop_A */  for(i=0; i<size; i++) 
  {
	a[i] = b[i];
  }

  /* Loop_B */  for(i=0; i<size; i++)
  {
	{;
//@ assert(a[i] == b[i]);
}

  }
}
