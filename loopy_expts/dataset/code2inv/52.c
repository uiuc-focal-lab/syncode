// Source: data/benchmarks/code2inv/52.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int c;
  
  (c = 0);
  
  while (unknown()) {
    {
      if ( unknown() ) {
        if ( (c != 4) )
        {
        (c  = (c + 1));
        }
      } else {
        if ( (c == 4) )
        {
        (c  = 1);
        }
      }

    }

  }
  
if ( (c < 0) )
if ( (c > 4) )
{;
//@ assert( (c == 4) );
}

}