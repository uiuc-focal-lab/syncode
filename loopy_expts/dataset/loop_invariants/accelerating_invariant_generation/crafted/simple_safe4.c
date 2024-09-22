// Source: data/benchmarks/accelerating_invariant_generation/crafted/simple_safe4.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 0x0ffffff0;

  while (x > 0) {
    x -= 2;
  }

  {;
//@ assert(!(x % 2));
}

}