// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark13_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int j = unknown_int();
  int k = unknown_int();
  
  if (!(i==0 && j==0)) return 0;
  while (i <= k) {
    i++;
    j=j+1;
  }
  {;
//@ assert(j==i);
}

  return 0;
}