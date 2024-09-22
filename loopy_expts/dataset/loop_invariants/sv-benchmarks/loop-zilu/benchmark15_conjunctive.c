// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark15_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int low = unknown_int();
  int mid = unknown_int();
  int high = unknown_int();
  if (!(low == 0 && mid >= 1 && high == 2*mid)) return 0;
  while (mid > 0) {
    low = low + 1;
    high = high - 1;
    mid = mid - 1;
  }
  {;
//@ assert(low == high);
}

  return 0;
}