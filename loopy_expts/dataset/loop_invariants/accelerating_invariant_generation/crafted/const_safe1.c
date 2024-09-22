// Source: data/benchmarks/accelerating_invariant_generation/crafted/const_safe1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 1;
  unsigned int y = 0;

  while (y < 10) {
    x = 0;
    y++;
  }

  {;
//@ assert(x == 0);
}

}