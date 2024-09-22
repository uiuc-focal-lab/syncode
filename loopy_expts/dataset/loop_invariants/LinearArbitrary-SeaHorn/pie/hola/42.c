// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/42.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();
extern int unknown2();

void main()
{
  int flag = unknown1();
  int x = 1;
  int y = 1;
  int a;
  
  if(flag)
    a = 0;
  else
    a = 1;

  while(unknown1()){
    if(flag)
    {
      a = x+y;
      x++;
    }
    else
    {
      a = x+y+1;
      y++;
    }
    if(a%2==1)
      y++;
    else
      x++;	  
  }
  
  if(flag)
    a++;
  {;
//@ assert(a%2==1);
}

}