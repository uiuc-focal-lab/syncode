// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark51_polynomial.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  
  if (!((x>=0) && (x<=50))) return 0;
  while (unknown_bool()) {
    if (x>50) x++;
    if (x == 0) { x ++;
    } else x--;
  }
  {;
//@ assert((x>=0) && (x<=50));
}

  return 0;
}