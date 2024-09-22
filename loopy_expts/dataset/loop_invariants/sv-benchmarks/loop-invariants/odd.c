// Source: data/benchmarks/sv-benchmarks/loop-invariants/odd.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main(void) {
  unsigned int x = 1;
  while (unknown_int()) {
    x += 2;
  }
  {;
//@ assert(x % 2);
}

  return 0;
}