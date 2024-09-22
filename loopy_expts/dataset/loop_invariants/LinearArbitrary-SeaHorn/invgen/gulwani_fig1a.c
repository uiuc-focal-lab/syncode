// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/gulwani_fig1a.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

void main() {
  int x,y;
  y = unknown();
  x = -50;
  while( x < 0 ) {
	x = x+y;
	y++;
  }
  {;
//@ assert(y>0);
}

}