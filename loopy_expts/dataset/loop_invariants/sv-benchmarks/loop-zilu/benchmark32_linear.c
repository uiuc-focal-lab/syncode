// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark32_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  
  if (!(x==1 || x==2)) return 0;
  while (unknown_bool()) {
    if(x==1) x=2;
    else if (x==2) x=1;
  }
  {;
//@ assert(x<=8);
}

  return 0;
}