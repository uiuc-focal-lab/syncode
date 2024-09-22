// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark18_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int k = unknown_int();
  int n = unknown_int();
  if (!((i==0) && (k==0) && (n>0))) return 0;
  while (i < n) {
    i++;k++;
  }
  {;
//@ assert((i == k) && (k == n));
}

  return 0;
}