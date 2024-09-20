// Source: data/benchmarks/code2inv/124.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int i;
  int j;
  int x;
  int y;
  
  (i = x);
  (j = y);
  
  while ((x != 0)) {
    {
    (x  = (x - 1));
    (y  = (y - 1));
    }

  }
  
if ( (i == j) )
{;
//@ assert( (y == 0) );
}

}