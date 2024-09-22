// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop11_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int unknown(){int x; return x;}

void errorFn() {ERROR: goto ERROR;}

void main()
{
  int e, s;

  e=0;
  s=2;
  while (unknown()) {
    if (s == 2){
      if (e ==0) e=1;
      s = 3;
    }
    else if (s == 3){
      if (e ==1) e=2;
      s=4;
    }
    else if (s == 4){
      {;
//@ assert(!( e == 3 ));
}

      s=5;
    }
  }
  
return;

}