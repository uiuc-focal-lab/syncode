// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop7_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int unknown(){int x; return x;}

void errorFn() {ERROR: goto ERROR;}

void main()
{
  int x, y;

  y = 0;
  x = 1;
  while ( unknown() < 10) {
    if (x<2) {
      x=2;
    } else {
      x=1;
    }
    if (y<1) {
      y=0;
    }
  }
  {;
//@ assert(!( x > 2 ));
}

return;

}