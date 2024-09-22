// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/20.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();

void main()
{
    int x, y, k, j, i, n;
    x = unknown1();
    y = unknown1();
    k = unknown1();
    j = unknown1();
    i = unknown1();
    n = unknown1();
    if((x+y)== k) {
    int m = 0;
    j = 0;
    while(j<n) {
      if(j==i)
      {
         x++;
         y--;
      }else
      {
         y++;
         x--;
      }
	if(unknown1())
  		m = j;
      j++;
    }
    {;
//@ assert((x+y)== k);
}

    if(n>0)
    {
   	{;
//@ assert(0<=m);
}
 
	{;
//@ assert(m<n);
}

    }
    }
}
