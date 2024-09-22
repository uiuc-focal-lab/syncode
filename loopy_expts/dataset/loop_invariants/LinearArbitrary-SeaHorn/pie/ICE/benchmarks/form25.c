// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/form25.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
  int x1,x2,x3,x4;
  int x1p,x2p,x3p,x4p, input;

  x1 = x2 = x3 = 0; x4 = -1;
  input = unknown_int();
  while(input)
  {
    x1p = unknown_int();
    x2p = unknown_int();
    x3p = unknown_int();
    x4p = unknown_int();

    if (x1p <= 0 && x1p >= x4p + 1 && x2p == x3p && (x4p >= 0 || x4p <= x3p))
    {
	x1 = x1p;
	x2 = x2p;
	x3 = x3p;
	x4 = x4p;
    }
    input = unknown_int();
  }
  {;
//@ assert(x1 <= 0 && x1 >= x4 + 1 && x2 == x3 && (x4 >= 0 || x4 <= x3));
}

}
