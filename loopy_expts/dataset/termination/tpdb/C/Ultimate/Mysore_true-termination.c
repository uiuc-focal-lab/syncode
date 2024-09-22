// Source: data/benchmarks/tpdb/C/Ultimate/Mysore_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	int x = unknown_int();
	int c = unknown_int();
	if (c < 2) {
		return 0;
	}
	while (x + c >= 0) {
		x = x - c;
		c = c + 1;
	}
	return 0;
}