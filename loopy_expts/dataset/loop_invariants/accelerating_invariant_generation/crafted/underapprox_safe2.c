// Source: data/benchmarks/accelerating_invariant_generation/crafted/underapprox_safe2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 0;
  unsigned int y = 1;

  while (x < 6) {
    x++;
    y *= 2;
  }

  {;
//@ assert(x == 6);
}

}