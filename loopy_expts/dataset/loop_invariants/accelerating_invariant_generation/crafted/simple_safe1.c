// Source: data/benchmarks/accelerating_invariant_generation/crafted/simple_safe1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 0;

  while (x < 0x0fffffff) {
    x += 2;
  }

  {;
//@ assert(!(x % 2));
}

}