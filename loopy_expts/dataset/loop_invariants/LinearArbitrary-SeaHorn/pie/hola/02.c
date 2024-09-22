// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/02.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown2();

int main()
{
	int i = 1;
	int j = 0;
	int z = i-j;
	int x = 0;
	int y = 0;
	int w = 0;

	while(unknown2()) 
	{
		z+=x+y+w;
		y++;
		if(z%2==1) 
		  x++;
		w+=2; 
	}

	{;
//@ assert(x==y);
}

}