// Source: data/benchmarks/code2inv/128.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int x;
  int y;
  
  (x = 1);
  
  while ((x < y)) {
    {
    (x  = (x + x));
    }

  }
  
{;
//@ assert( (x >= 1) );
}

}