// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/22.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();

void main()
{
  int x = 0;
  int y = 0;
  int z = 0;
  int k = 0;

  while(unknown1())
  {
     if(k%3 == 0)
       x++;
     y++;
     z++;
     k = x+y+z;
  }

  {;
//@ assert(x==y && y==z);
}
 
}
