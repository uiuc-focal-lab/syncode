// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark08_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int n = unknown_int();
  int sum = unknown_int();
  int i = unknown_int();
  
  if (!(n>=0 && sum==0 && i==0)) return 0;
  while (i<n) {
    sum=sum+i;
    i++;
  }
  {;
//@ assert(sum>=0);
}

  return 0;
}