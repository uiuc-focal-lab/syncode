// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark47_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  if (!(x<y)) return 0;
  while (x<y) {
    if (x < 0) x = x + 7;
    else x = x + 10;
    if (y < 0) y = y - 10;
    else y = y + 3;
  }
  {;
//@ assert(x >= y && x <= y + 16);
}

  return 0;
}