// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop29_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
int main() {
  int x = 0;
  while(x < 100) {
    x++;
    if(x == 50)
      break;
  }
  {;
//@ assert(!( x != 50 ));
}

}