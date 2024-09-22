// Source: data/benchmarks/code2inv/116.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int sn;
  int v1;
  int v2;
  int v3;
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