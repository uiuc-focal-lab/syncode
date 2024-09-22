// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop4_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
void main(){
  int x,N;
  int a;

  a=0;
  N =10;
  x = 0;
  do {
    x=x+1;
  } while (x != N);

  {;
//@ assert(!( a > 1 ));
}

}