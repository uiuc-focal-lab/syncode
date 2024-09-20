// Source: data/benchmarks/code2inv/12.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int x;
  int y;
  int z1;
  int z2;
  int z3;
  
  assume((x >= 0));
  assume((x <= 10));
  assume((y <= 10));
  assume((y >= 0));
  
  while (unknown()) {
    {
    (x  = (x + 10));
    (y  = (y + 10));
    }

  }
  
if ( (y == 0) )
{;
//@ assert( (x != 20) );
}

}