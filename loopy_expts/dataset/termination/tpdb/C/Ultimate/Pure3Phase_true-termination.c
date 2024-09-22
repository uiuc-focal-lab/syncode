// Source: data/benchmarks/tpdb/C/Ultimate/Pure3Phase_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	int x = unknown_int();
	int y = unknown_int();
	int z = unknown_int();
	while (x >= 0) {
		if (unknown_int()) {
			x = x + y;
		} else {
			x = x + z;
		}
		y = y + z;
		z = z - 1;
	}
	return 0;
}