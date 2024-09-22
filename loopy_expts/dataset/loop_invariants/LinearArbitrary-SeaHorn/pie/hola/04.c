// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/04.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();

void main() {
  int x,y;

  x = -50;
  
  while( x < 0 ) {
	x = x+y;
	y++;
  }
  {;
//@ assert(y>0);
}

}
