// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/form27.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
  int x1,x2,x3,x4,x5;
  int x1p,x2p,x3p,x4p,x5p, input;

  x1 = x2 = x3 = x4 = x5 = 0;
  input = unknown_int();
  while(input)
  {
    x1p = unknown_int();
    x2p = unknown_int();
    x3p = unknown_int();
    x4p = unknown_int();
    x5p = unknown_int();

    if (0 <= x1p && x1p <= x4p + 1 && x2p == x3p && (x2p <= -1 || x4p <= x2p + 2) && x5p == 0)
    {
	x1 = x1p;
	x2 = x2p;
	x3 = x3p;
	x4 = x4p;
	x5 = x5p;
    }
    input = unknown_int();
  }
  {;
//@ assert(0 <= x1 && x1 <= x4 + 1 && x2 == x3 && (x2 <= -1 || x4 <= x2 + 2) && x5 == 0);
}

}
