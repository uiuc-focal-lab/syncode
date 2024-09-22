// Source: data/benchmarks/tpdb/C/Ultimate/Bangalore_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	int x = unknown_int();
	int y = unknown_int();
	if (y < 1) {
		return 0;
	}
	while (x >= 0) {
		x = x - y;
	}
	return 0;
}
