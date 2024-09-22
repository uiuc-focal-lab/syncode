// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark14_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  
  if (!(i>=0 && i<=200)) return 0;
  while (i>0) {
    i--;
  }
  {;
//@ assert(i>=0);
}

  return 0;
}