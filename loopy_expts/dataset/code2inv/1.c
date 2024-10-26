// Source: data/benchmarks/code2inv/1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int x;
  int y;
  
  (x = 1);
  (y = 0);
  
  /*@ 
    loop invariant 0 <= y <= 100000;
    loop invariant x >= (1 + (y - 1) * y / 2);
  */
  while ((y < 100000)) {
    {
    (x  = (x + y));
    (y  = (y + 1));
    }

  }
  //@ assert( (x >= y) );
}