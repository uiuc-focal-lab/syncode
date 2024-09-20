// Source: data/benchmarks/code2inv/25.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int x;
  
  (x = 10000);
  
  while ((x > 0)) {
    {
    (x  = (x - 1));
    }

  }
  
{;
//@ assert( (x == 0) );
}

}