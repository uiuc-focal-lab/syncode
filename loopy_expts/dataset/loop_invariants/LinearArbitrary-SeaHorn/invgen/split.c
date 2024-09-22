// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/split.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

void main() {
  int k = 100;
  int b = 0;
  int i;
  int j;
  int n;
  i = j = 0;
  for( n = 0 ; n < 2*k ; n++ ) {
    
    if(b) {
      i++;
    } else {
      j++;
    }
    b = !b;
  }
  {;
//@ assert(i == j);
}

}