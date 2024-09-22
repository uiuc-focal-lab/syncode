// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark41_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  int z = unknown_int();
  if (!(x == y && y == 0 && z==0)) return 0;
  while (unknown_bool()) {
    x++;y++;z-=2;
  }
  {;
//@ assert(x == y && x >= 0 && x+y+z==0);
}

  return 0;
}