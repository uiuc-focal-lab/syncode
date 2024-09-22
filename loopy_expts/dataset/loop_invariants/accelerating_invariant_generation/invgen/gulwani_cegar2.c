// Source: data/benchmarks/accelerating_invariant_generation/invgen/gulwani_cegar2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int __BLAST_NONDET;
void main() {
  int x,m,n;

  x = 0;
  m = 0;
  while( x < n ) {
    if(__BLAST_NONDET)
	m = x;
	x++;
  }
  if( n > 0 )
    {
      {;
//@ assert( 0<=m);
}

      {;
//@ assert(m<n);
}

    }
}