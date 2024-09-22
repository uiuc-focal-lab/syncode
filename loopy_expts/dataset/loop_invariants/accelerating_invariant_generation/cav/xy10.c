// Source: data/benchmarks/accelerating_invariant_generation/cav/xy10.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet(){
  int x;
  return x;
}

int main ()
{
  int x = 0;
  int y = 0;
  int z;

  while (unknown_int()){
    x += 10;
    y += 1;
  }

  if (x <= z && y >= z + 1)
    goto ERROR;

return 0;

  { ERROR: {; 
//@ assert(\false);
}
}
}