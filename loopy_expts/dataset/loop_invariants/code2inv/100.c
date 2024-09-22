// Source: data/benchmarks/code2inv/100.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int n;
  int x;
  int y;
  
  assume((n >= 0));
  (x = n);
  (y = 0);
  
  while ((x > 0)) {
    {
    (y  = (y + 1));
    (x  = (x - 1));
    }

  }
  
{;
//@ assert( (y == n) );
}

}