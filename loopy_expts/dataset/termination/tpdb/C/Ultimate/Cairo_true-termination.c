// Source: data/benchmarks/tpdb/C/Ultimate/Cairo_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	int x = unknown_int();
	if (x <= 0) {
		return 0;
	}
	while (x != 0) {
		x = x - 1;
	}
	return 0;
}