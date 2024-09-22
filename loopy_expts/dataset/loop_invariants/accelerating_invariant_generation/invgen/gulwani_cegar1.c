// Source: data/benchmarks/accelerating_invariant_generation/invgen/gulwani_cegar1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int __BLAST_NONDET;
void main() {
  int x,y;

  assume(0 <= x);  assume(x <= 2);
  assume(0 <= y);  assume(y <= 2);
  while( __BLAST_NONDET ) {
	x+=2;
	y+=2;
  }
  if( y >= 0 ) 
    if( y <= 0 ) 
      if( 4 <= x ) 
	{;
//@ assert( x < 4 );
}

}