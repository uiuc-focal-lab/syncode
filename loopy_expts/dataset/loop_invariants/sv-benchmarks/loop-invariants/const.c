// Source: data/benchmarks/sv-benchmarks/loop-invariants/const.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main(void) {
  unsigned int s = 0;
  while (unknown_uint()) {
    if (s != 0) {
      ++s;
    }
    if (unknown_uint()) {
      {;
//@ assert(s == 0);
}

    }
  }
  return 0;
}