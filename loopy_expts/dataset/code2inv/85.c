// Source: data/benchmarks/code2inv/85.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int x;
  int y;
  int z1;
  int z2;
  int z3;
  
  (x = -15000);
  
  while ((x < 0)) {
    {
    (x  = (x + y));
    (y  = (y + 1));
    }

  }
  
{;
//@ assert( (y > 0) );
}

}