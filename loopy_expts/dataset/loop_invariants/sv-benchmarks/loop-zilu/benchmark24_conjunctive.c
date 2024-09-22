// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark24_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int k = unknown_int();
  int n = unknown_int();
  
  if (!(i==0 && k==n && n>=0)) return 0;
  while (i<n) {
    k--;
    i+=2;
  }
  {;
//@ assert(2*k>=n-1);
}

  return 0;
}