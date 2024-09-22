// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop6_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

;

void errorFn() {ERROR: goto ERROR;}
void main()
{
  int i,x,y,NONDET,z;

  x=0;
  z=1;
  y = unknown_uint();

  assume( y>=0 );
  i = 0;
  while (i < 10) {
    if (NONDET > 0) {
      x = x;
    } else {
      x++;
    }

    {;
//@ assert(!( y < 0 ));
}

    i++;
  }
  {;
//@ assert(!( z<0 ));
}

}