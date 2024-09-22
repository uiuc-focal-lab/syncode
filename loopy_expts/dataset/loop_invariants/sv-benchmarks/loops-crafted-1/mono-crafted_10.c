// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/mono-crafted_10.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void)
{
	unsigned int x = 0;
	unsigned int y = 10000000;
	unsigned int z=5000000;
	while(x<y){	
		if(x>=5000000)
			z++;
		x++;
	}
	{;
//@ assert(z==x);
}

	return 0;
}