// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark48_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int j = unknown_int();
  int k = unknown_int();
  if (!(i<j && k> 0)) return 0;
  while (i<j) {
    k=k+1;i=i+1;
  }
  {;
//@ assert(k > j - i);
}

  return 0;
}