// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop2_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
void main(){

  int NONDET;
  int i,N;
  int a;
  int x;

  if (NONDET > 0) x=1; else x=2;

  while (i<N){
    i=i+1;
  }

  {;
//@ assert(!( x >2 ));
}

return;

}