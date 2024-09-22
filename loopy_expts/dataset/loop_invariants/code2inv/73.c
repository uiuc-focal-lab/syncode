// Source: data/benchmarks/code2inv/73.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int c;
  int y;
  int z;
  
  (c = 0);
  assume((y >= 0));
  assume((y >= 127));
  (z = (36 * y));
  
  while (unknown()) {
    if ( (c < 36) )
    {
    (z  = (z + 1));
    (c  = (c + 1));
    }

  }
  
if ( (z < 0) )
if ( (z >= 4608) )
{;
//@ assert( (c >= 36) );
}

}