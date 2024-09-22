// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/19.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();

void main()
{
  int n = unknown1 (); 
  int m = unknown1 ();
  if (n >= 0 && m >= 0 && m < n) {
  int x=0; 
  int y=m;
  while(x<n) {
    x++;
    if(x>m) y++;
  }
  {;
//@ assert(y==n);
}

  }
}