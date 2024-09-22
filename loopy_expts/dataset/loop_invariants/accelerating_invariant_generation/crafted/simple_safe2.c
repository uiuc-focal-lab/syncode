// Source: data/benchmarks/accelerating_invariant_generation/crafted/simple_safe2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x;

  while (x < 0x0fffffff) {
    x++;
  }

  {;
//@ assert(x >= 0x0fffffff);
}

}