// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/05.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();
extern int unknown2();

void main()
{
	int flag = unknown1();
	int x = 0;
	int y = 0;

	int j = 0;
	int i = 0;

	while(unknown2())
	{
	  x++;
	  y++;
	  i+=x;
	  j+=y;
	  if(flag)  j+=1;
	} 
	{;
//@ assert(j>=i);
}

}