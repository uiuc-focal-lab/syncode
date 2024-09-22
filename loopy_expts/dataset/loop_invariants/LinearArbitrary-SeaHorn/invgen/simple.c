// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/simple.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

void main() {
  int x=0;
  int n = unknown();
  
  assume(n > 0 );
  while( x < n ){
    x++;
  }
  {;
//@ assert( x<=n );
}

}