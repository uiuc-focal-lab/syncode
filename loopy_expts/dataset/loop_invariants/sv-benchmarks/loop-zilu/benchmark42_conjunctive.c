// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark42_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  int z = unknown_int();
  if (!(x == y && x >= 0 && x+y+z==0)) return 0;
  while (x > 0) {
    x--;
    y--;
    z++;
    z++;
  }
  {;
//@ assert(z<=0);
}

  return 0;
}