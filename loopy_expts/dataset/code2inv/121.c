// Source: data/benchmarks/code2inv/121.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int i;
  int sn;
  
  (sn = 0);
  (i = 1);
  
  while ((i <= 8)) {
    {
    (i  = (i + 1));
    (sn  = (sn + 1));
    }

  }
  
if ( (sn != 0) )
{;
//@ assert( (sn == 8) );
}

}