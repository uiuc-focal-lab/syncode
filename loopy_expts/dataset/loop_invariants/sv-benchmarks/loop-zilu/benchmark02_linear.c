// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark02_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int n = unknown_int();
  int i = unknown_int();
  int l = unknown_int();
  i = l;
  if (!(l>0)) return 0;
  while (i < n) {
    i++;
  }
  {;
//@ assert(l>=1);
}

  return 0;
}