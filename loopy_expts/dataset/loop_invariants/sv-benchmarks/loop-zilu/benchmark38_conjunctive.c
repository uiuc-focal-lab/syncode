// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark38_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  if (!(x == y && y == 0)) return 0;
  while (unknown_bool()) {
    x+=4;y++;
  }
  {;
//@ assert(x == 4*y && x >= 0);
}

  return 0;
}