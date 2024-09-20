// Source: data/benchmarks/code2inv/93.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int i;
  int n;
  int x;
  int y;
  
  assume((n >= 0));
  (i = 0);
  (x = 0);
  (y = 0);
  
  while ((i < n)) {
    {
    (i  = (i + 1));
      if ( unknown() ) {
        {
        (x  = (x + 1));
        (y  = (y + 2));
        }
      } else {
        {
        (x  = (x + 2));
        (y  = (y + 1));
        }
      }

    }

  }
  
{;
//@ assert( ((3 * n) == (x + y)) );
}

}