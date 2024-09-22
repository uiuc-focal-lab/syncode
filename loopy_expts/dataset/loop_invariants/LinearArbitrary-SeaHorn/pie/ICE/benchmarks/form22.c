// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/form22.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
  int x1,x2,x3;
  int x1p,x2p,x3p, input;

  x1 = x2 = x3 = 0;
  input = unknown_int();
  while(input)
  {
    x1p = unknown_int();
    x2p = unknown_int();
    x3p = unknown_int();

    if (x1p <= x2p && (x2p >= 0 || x2p - x3p <= 2))
    {
	x1 = x1p;
	x2 = x2p;
	x3 = x3p;
    }
    input = unknown_int();
  }
  {;
//@ assert(x1 <= x2 && (x2 >= 0 || x2 - x3 <= 2));
}
    
}
