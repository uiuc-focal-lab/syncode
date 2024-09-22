// Source: data/benchmarks/accelerating_invariant_generation/crafted/diamond_safe1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 0;
  unsigned int y;

  while (x < 99) {
    if (y % 2 == 0) {
      x += 2;
    } else {
      x++;
    }
  }

  {;
//@ assert((x % 2) == (y % 2));
}

}