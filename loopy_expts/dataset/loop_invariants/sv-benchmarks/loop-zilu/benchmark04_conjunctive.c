// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark04_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int k = unknown_int();
  int j = unknown_int();
  int n = unknown_int();
  
  if (!(n>=1 && k>=n && j==0)) return 0;
  while (j<=n-1) {
    j++;
    k--;
  }
  {;
//@ assert(k>=0);
}

  return 0;
}