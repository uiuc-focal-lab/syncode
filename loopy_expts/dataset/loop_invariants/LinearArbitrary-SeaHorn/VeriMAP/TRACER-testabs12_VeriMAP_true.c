// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testabs12_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

;

void errorFn() {ERROR: goto ERROR;}
int main(){
  int i,count,n;
  count = unknown_uint();
  assume( count >= 0 );
  i=0;

  while (i < 100 ){
      count++;
      i++;
  }

  {;
//@ assert(!( (i > 100 ) || count < 0 ));
}

}