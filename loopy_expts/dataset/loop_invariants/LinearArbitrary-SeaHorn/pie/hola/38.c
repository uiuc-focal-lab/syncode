// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/38.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

void main()
{
  int x=0;
  int y=0;
  int i=0;
  int n = unknown();
  
  while(i<n) {
    i++;
    x++;
    if(i%2 == 0) y++;
  }
  
  if(i%2 == 0) {;
//@ assert(x==2*y);
}

}
