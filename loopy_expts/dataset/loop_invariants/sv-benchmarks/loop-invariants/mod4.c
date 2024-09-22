// Source: data/benchmarks/sv-benchmarks/loop-invariants/mod4.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main(void) {
  unsigned int x = 0;
  while (unknown_int()) {
    x += 4;
  }
  {;
//@ assert(!(x % 4));
}

  return 0;
}