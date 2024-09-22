// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/43.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();
extern int unknown2();
extern int unknown3();

int main()
{
  int x = unknown1();
  int y = unknown2();
  int i=0;
  int t=y;
   
  if (x==y) return x;
  
  while (unknown3()){
    if (x > 0)   
      y = y + x;
  }
   
  {;
//@ assert(y>=t);
}

}
