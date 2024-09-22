// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/mono-crafted_9.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main()
{
	int x = 0;
	int y = 500000;
	while(x < 1000000) {
		if (x < 500000) {
			x = x + 1;
		} else {
			x = x + 1;
			y = y + 1;
		}
	}
	{;
//@ assert(y==x);
}

	return 0;
}