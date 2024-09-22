// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Thun_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
	int x;
	int y;
	x = unknown_int();
	y = unknown_int();
	while (x >= 0) {
		x = x + y;
		y = (-2)*y - 1;
	}
	return 0;
}