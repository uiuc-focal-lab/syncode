// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark12_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  int t = unknown_int();
  
  if (!(x!=y && y==t)) return 0;
  while (unknown_bool()) {
    if(x>0) y=y+x;
  }
  {;
//@ assert(y>=t);
}

  return 0;
}