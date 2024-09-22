// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark46_disjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  int z = unknown_int();
  if (!(y>0 || x>0 || z>0)) return 0;
  while (unknown_bool()) {
    if (x>0) {
      x++;
    }
    if (y>0) {
      y++;
    } else {
      z++;
    }
  }
  {;
//@ assert(x>0 || y>0 || z>0);
}

  return 0;
}