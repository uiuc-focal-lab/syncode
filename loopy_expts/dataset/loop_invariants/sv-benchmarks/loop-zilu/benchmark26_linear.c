// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark26_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  if (!(x<y)) return 0;
  while (x<y) {
    x=x+1;
  }
  {;
//@ assert(x==y);
}

  return 0;
}