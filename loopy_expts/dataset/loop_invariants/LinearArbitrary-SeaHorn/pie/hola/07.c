// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/07.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1 ();
extern int unknown2 ();

int main() {
  int i, n, a, b;
  n = unknown1 ();
  i = 0; a = 0; b = 0;

  if (n >= 0) {
  	while( i < n ) {
    		if(unknown2()) {
      			a = a+1;
      			b = b+2;
    		} else {
      			a = a+2;
      			b = b+1;
    		}
    		i = i+1;
  	}
  	{;
//@ assert( a+b == 3*n );
}

  }

  return 0;
}