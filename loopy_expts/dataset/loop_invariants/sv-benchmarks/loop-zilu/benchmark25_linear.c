// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark25_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  if (!(x<0)) return 0;
  while (x<10) {
    x=x+1;
  }
  {;
//@ assert(x==10);
}

  return 0;
}