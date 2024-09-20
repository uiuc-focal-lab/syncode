// Source: data/benchmarks/code2inv/36.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int c;
  
  (c = 0);
  
  while (unknown()) {
    {
      if ( unknown() ) {
        if ( (c != 40) )
        {
        (c  = (c + 1));
        }
      } else {
        if ( (c == 40) )
        {
        (c  = 1);
        }
      }

    }

  }
  
if ( (c != 40) )
{;
//@ assert( (c <= 40) );
}

}