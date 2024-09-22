// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark16_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int k = unknown_int();
  if (!(0 <= k && k <= 1 && i == 1)) return 0;
  while (unknown_bool()) {
    i = i + 1;
    k = k - 1;
  }
  {;
//@ assert(1 <= i + k && i + k <= 2 && i >= 1);
}

  return 0;
}