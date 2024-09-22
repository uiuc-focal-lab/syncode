// Source: data/benchmarks/code2inv/24.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int i;
  int j;
  
  (i = 1);
  (j = 10);
  
  while ((j >= i)) {
    {
    (i  = (i + 2));
    (j  = (j - 1));
    }

  }
  
{;
//@ assert( (j == 6) );
}

}