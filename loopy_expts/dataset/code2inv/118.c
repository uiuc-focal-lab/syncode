// Source: data/benchmarks/code2inv/118.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int i;
  int size;
  int sn;
  
  (sn = 0);
  (i = 1);
  
  while ((i <= size)) {
    {
    (i  = (i + 1));
    (sn  = (sn + 1));
    }

  }
  
if ( (sn != size) )
{;
//@ assert( (sn == 0) );
}

}