// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Copenhagen_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x, y, oldx;
	x = unknown_int();
	y = unknown_int();
	while (x >= 0 && y >= 0) {
		oldx = x;
		x = y - 1;
		y = oldx - 1;
	}
	return 0;
}