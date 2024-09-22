// Source: data/benchmarks/accelerating_invariant_generation/invgen/up-nested.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int NONDET;

void main() {
  int n,j,i,k;

  i = 0;
  k = 0;

  assume ( j<=n );
  while ( j <= n ) {
    
    assume( i >= 0);
    
    j++;
  }
  {;
//@ assert( i>= 0);
}

}