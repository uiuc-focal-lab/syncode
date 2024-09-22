// Source: data/benchmarks/code2inv/133.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int n;
  int x;
  
  (x = 0);
  assume((n >= 0));
  
  while ((x < n)) {
    {
    (x  = (x + 1));
    }

  }
  
{;
//@ assert( (x == n) );
}

}