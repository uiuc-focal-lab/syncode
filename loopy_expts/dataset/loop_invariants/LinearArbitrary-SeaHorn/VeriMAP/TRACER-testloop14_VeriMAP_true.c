// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop14_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

void errorFn() {ERROR: goto ERROR;}
int main()
{
  int i, x, y;
  x = unknown_uint();
  y = unknown_uint();
  if (y <= 2) {
    if (x < 0) {
      x = 0;
    }
    i = 0;
    while (i < 10) {
      {;
//@ assert(!( y > 2 ));
}

      i++;
    }

    {;
//@ assert(!( x <= -1 ));
}

  }
  return 0;
}