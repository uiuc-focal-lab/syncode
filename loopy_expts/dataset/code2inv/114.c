// Source: data/benchmarks/code2inv/114.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int sn;
  int x;
  
  (sn = 0);
  (x = 0);
  
  while (unknown()) {
    {
    (x  = (x + 1));
    (sn  = (sn + 1));
    }

  }
  
if ( (sn != x) )
{;
//@ assert( (sn == -1) );
}

}