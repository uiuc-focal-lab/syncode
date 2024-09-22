// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testabs15_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
int main(int n){
  int i, a, b;
  int TRACER_NONDET;

  if(n >=0){

    i=0; a=0; b=0;

    while (i < n){
      if (TRACER_NONDET){
 a=a+1;
 b=b+2;
      }
      else{
 a=a+2;
 b=b+1;
      }
      i++;
    }
    {;
//@ assert(!( a+b != 3*n ));
}

  }
}