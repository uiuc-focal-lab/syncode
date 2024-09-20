// Source: data/benchmarks/code2inv/88.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int lock;
  int x;
  int y;
  
  (y = (x + 1));
  (lock = 0);
  
  while ((x != y)) {
    {
      if ( unknown() ) {
        {
        (lock  = 1);
        (x  = y);
        }
      } else {
        {
        (lock  = 0);
        (x  = y);
        (y  = (y + 1));
        }
      }

    }

  }
  
{;
//@ assert( (lock == 1) );
}

}