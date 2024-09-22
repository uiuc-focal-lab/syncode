// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark49_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int j = unknown_int();
  int r = unknown_int();
  if (!(r > i + j)) return 0;
  while (i > 0) {
    i = i - 1;
    j = j + 1;
  }
  {;
//@ assert(r > i + j);
}

  return 0;
}