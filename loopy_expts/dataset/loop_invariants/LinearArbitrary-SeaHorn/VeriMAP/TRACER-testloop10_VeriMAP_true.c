// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop10_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);
extern unsigned int unknown_uint(void);

int unknown(){int x; return x;}

void errorFn() {ERROR: goto ERROR;}

void main()
{
  int lock, old, new;
  old = unknown_uint();
  lock=0;
  new=old+1;

  while (new != old) {
    lock = 1;
    old = new;
    if (unknown()) {
      lock = 0;
      new++;
    }
  }

  {;
//@ assert(!( lock==0 ));
}

return;

}