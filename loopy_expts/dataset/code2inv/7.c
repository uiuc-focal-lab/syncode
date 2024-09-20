// Source: data/benchmarks/code2inv/7.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int x;
  int y;
  
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
  
if ( (x == 20) )
{;
//@ assert( (y != 0) );
}

}