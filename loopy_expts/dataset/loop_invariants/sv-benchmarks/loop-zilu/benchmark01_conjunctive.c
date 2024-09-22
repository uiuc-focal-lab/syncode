// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark01_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  
  if (!(x==1 && y==1)) return 0;
  while (unknown_bool()) {
    x=x+y;
    y=x;
  }
  {;
//@ assert(y>=1);
}

  return 0;
}