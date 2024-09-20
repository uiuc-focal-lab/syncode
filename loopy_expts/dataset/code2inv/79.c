// Source: data/benchmarks/code2inv/79.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int i;
  int x;
  int y;
  
  (i = 0);
  assume((x >= 0));
  assume((y >= 0));
  assume((x >= y));
  
  while (unknown()) {
    if ( (i < y) )
    {
    (i  = (i + 1));
    }

  }
  
if ( (i >= x) )
if ( (0 > i) )
{;
//@ assert( (i >= y) );
}

}