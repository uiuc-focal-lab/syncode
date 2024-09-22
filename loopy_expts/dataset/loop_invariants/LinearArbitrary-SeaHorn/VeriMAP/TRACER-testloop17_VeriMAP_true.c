// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop17_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

;

void errorFn() {ERROR: goto ERROR;}
int main()
{
	int N = unknown_uint();
  int i, j, k;

  i = 0;
  j = 0;
  k = 0;

  assume( N > 1 );

  while (i < N) {
    if (i<1)
      k = 1;
    else
      k = 0;
    j++;
    i++;
  }

  {;
//@ assert(!( k>0 ));
}

  return 0;
}