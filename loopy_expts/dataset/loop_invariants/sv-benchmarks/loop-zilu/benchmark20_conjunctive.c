// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark20_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int n = unknown_int();
  int sum = unknown_int();
  
  if (!(i==0 && n>=0 && n<=100 && sum==0)) return 0;
  while (i<n) {
    sum = sum + i;
    i++;
  }
  {;
//@ assert(sum>=0);
}

  return 0;
}