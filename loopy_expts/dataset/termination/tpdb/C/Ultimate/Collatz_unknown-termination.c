// Source: data/benchmarks/tpdb/C/Ultimate/Collatz_unknown-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	int y = unknown_int();
	while (y > 1) {
		if (y % 2 == 0) {
			y = y / 2;
		} else {
			y = 3*y + 1;
		}
	}
	return 0;
}