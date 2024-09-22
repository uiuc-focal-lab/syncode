// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark31_disjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  if (!(x < 0)) return 0;
  while (1) {
    if (x>=0) {
      break;
    } else {
      x=x+y; y++;
    }
  }
  {;
//@ assert(y>=0);
}

  return 0;
}