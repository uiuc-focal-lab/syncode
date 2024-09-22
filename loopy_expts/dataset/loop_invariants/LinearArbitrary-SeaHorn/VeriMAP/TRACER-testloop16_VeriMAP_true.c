// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop16_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
void main(int N)
{
  int i, x;

  x = 1;
  i = 0;

  while (i<N) {
    if (x==1) {
      x=2;
    } else {
      x=1;
    }
    i++;
  }

  {;
//@ assert(!( x>2 ));
}

return;

}