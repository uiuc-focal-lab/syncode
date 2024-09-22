// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/ken-imp.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

void main() {
  int i = unknown();
  int j = unknown();
  int x = i;
  int y = j;
  while(x!=0) {
	x--;
	y--;
  }
  if(i==j)
	if(y != 0) { ERROR: {; 
//@ assert(\false);
}
}
}