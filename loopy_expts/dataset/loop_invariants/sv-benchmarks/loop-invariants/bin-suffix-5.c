// Source: data/benchmarks/sv-benchmarks/loop-invariants/bin-suffix-5.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main(void) {
  unsigned int x = 5;
  while (unknown_int()) {
    x += 8;
  }
  {;
//@ assert((x & 5) == 5);
}

  return 0;
}