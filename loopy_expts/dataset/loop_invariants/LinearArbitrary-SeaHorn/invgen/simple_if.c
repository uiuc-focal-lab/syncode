// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/simple_if.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void main() {
  int n,m;
  n = unknown ();
  m = unknown ();
  int i = 1;
   
  while( i < n ) {
    if( m > 0 ) {
      i = 2*i;
    } else {
      i = 3*i;
    }
    
  }
  {;
//@ assert(i > 0 );
}

}