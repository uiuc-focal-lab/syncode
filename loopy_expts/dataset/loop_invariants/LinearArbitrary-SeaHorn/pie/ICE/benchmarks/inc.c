// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/inc.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
  int x, m;
  x = 0;
  while(x < 100)
  {
    m = unknown_int();
    x = x + 1;
  }
  {;
//@ assert(x == 100);
}
    
}
