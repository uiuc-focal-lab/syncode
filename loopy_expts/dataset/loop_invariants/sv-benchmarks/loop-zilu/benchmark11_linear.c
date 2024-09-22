// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark11_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int n = unknown_int();
  
  if (!(x==0 && n>0)) return 0;
  while (x<n) {
    x++;
  }
  {;
//@ assert(x==n);
}

  return 0;
}