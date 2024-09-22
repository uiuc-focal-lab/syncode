// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark23_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

int main() {
  int i = unknown_int();
  int j = unknown_int();
  
  if (!(i==0 && j==0)) return 0;
  while (i<100) {
    j+=2;
    i++;
  }
  {;
//@ assert(j==200);
}

  return 0;
}