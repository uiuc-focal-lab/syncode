// Source: data/benchmarks/sv-benchmarks/loop-invariants/eq1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main(void) {
  unsigned int w = unknown_uint();
  unsigned int x = w;
  unsigned int y = unknown_uint();
  unsigned int z = y;
  while (unknown_uint()) {
    if (unknown_uint()) {
      ++w; ++x;
    } else {
      --y; --z;
    }
  }
  {;
//@ assert(w == x && y == z);
}

  return 0;
}