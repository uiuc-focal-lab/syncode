// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark10_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int c = unknown_int();
  
  if (!(c==0 && i==0)) return 0;
  while (i<100) {
    c=c+i;
    i=i+1;
    if (i<=0) break;
  }
  {;
//@ assert(c>=0);
}

  return 0;
}