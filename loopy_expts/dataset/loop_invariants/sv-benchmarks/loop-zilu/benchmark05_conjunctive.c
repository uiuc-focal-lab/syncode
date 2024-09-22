// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark05_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  int n = unknown_int();
  
  if (!(x>=0 && x<=y && y<n)) return 0;
  while (x<n) {
    x++;
    if (x>y) y++;
  }
  {;
//@ assert(y==n);
}

  return 0;
}