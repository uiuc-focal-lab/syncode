// Source: data/benchmarks/dillig/safe/3.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

/*@ requires size > 0;
 requires num_to_init > 0;
*/
void main(int* a, int size, int num_to_init)
{
  assume(num_to_init <= size);
  int i;
  /* Loop_A */  for(i=0; i<num_to_init; i++) 
  {
	a[i] = 0;
  }

  /* Loop_B */  for(i=0; i<num_to_init; i++)
  {
	{;
//@ assert(a[i] == 0);
}

  }
}
