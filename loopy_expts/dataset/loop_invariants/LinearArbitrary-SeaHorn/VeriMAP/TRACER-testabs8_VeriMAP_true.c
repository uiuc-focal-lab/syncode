// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testabs8_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
int main(int n){
  int i;

  i=0;n=10;

  while (i < n){ i++; }

  {;
//@ assert(!( i>10 ));
}

}