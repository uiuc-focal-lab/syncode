// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark33_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  
  if (!(x>=0)) return 0;
  while (x<100 && x>=0) {
    x++;
  }
  {;
//@ assert(x>=100);
}

  return 0;
}