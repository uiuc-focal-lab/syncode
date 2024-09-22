// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/21.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();
extern int unknown2();

int main() {
  int c1 = 4000;
  int c2 = 2000;
  int n, v;
  int i, k, j;

  n = unknown1();

  assume (n > 0 && n < 10);

  k = 0;
  i = 0;
  while( i < n ) {
    i++;
    if(unknown2() % 2 == 0) 
      v = 0;
    else v = 1;
    
    if( v == 0 )
      k += c1;
    else 
      k += c2;
  }
  
  {;
//@ assert(k>n);
}

  return 0;
}
