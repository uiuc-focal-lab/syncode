// Source: data/benchmarks/accelerating_invariant_generation/invgen/split.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void main() {
  int k = 100;
  int b;
  int i;
  int j;
  int n;
  i = j;
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