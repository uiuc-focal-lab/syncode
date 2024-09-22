// Source: data/benchmarks/sv-benchmarks/loop-invariants/eq2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main(void) {
  unsigned int w = unknown_uint();
  unsigned int x = w;
  unsigned int y = w + 1;
  unsigned int z = x + 1;
  while (unknown_uint()) {
    y++;
    z++;
  }
  {;
//@ assert(y == z);
}

  return 0;
}