// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/MenloPark_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x, y, z;
	x = unknown_int();
	y = 100;
	z = 1;
	while (x >= 0) {
		x = x - y;
		y = y - z;
		z = -z;
	}
	return 0;
}