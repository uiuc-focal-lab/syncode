// Source: data/benchmarks/tpdb/C/Ultimate/Parallel_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	int x = unknown_int();
	int y = unknown_int();
	while (1) {
		if (x >= 0) {
			x = x - 1;
		} else {
			if (y < 0) {
				break;
			}
			y = y - 1;
		}
	}
	return 0;
}