// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark50_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int xa = unknown_int();
  int ya = unknown_int();
  if (!(xa + ya > 0)) return 0;
  while (xa > 0) {
    xa--;
    ya++;
  }
  {;
//@ assert(ya >= 0);
}

  return 0;
}