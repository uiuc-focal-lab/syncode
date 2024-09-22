// Source: data/benchmarks/code2inv/103.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int x;
  
  (x = 0);
  
  while ((x < 100)) {
    {
    (x  = (x + 1));
    }

  }
  
{;
//@ assert( (x == 100) );
}

}