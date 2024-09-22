// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop1_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
void main(){

  int NONDET;
  int i,N;
  int a;
  int x;

  x=0;
  i=0;

  if (NONDET > 0) a=1; else a=2;

  while (i<N){
    i=i+1;
  }

  {;
//@ assert(!( x >0 ));
}

return;

}