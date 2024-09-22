// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/32.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

void main() {
  int k = 100;
  int b = 0;
  int i = unknown();
  int j = unknown();
  int n;
  i = j = 0;
  for( n = 0 ; n < 2*k ; n++ ) {
    if((int )b == 1) {
      i++;
      b = 0;
    } else if ((int )b == 0) {
      j++;
      b = 1;
    } 
    
  }
  {;
//@ assert(i == j);
}

}