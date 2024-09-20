// Source: data/benchmarks/code2inv/83.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int x;
  int y;
  
  (x = -5000);
  
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