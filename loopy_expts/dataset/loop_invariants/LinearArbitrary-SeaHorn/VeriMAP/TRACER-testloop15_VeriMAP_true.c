// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop15_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
int main()
{
  int i = 0;
  int N = 100;

  while (i<N) {
    i++;
  }

  {;
//@ assert(!( i>N ));
}

  return 0;
}