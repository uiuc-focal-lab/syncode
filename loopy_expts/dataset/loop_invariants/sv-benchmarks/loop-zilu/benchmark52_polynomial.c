// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark52_polynomial.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  if (!(i < 10 && i > -10)) return 0;
  while (i * i < 100) {
    i = i + 1;
  }
  {;
//@ assert(i == 10);
}

  return 0;
}