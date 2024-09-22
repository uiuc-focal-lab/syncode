// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/01.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();

void main()
{
 int x=1; int y=1;
 while(unknown1()) {
   int t1 = x;
   int t2 = y;
   x = t1+ t2;
   y = t1 + t2;
 }
 {;
//@ assert(y>=1);
}

}
