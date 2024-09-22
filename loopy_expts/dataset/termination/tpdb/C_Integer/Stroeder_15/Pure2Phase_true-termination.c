// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Pure2Phase_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int y, z;
	y = unknown_int();
	z = unknown_int();
	while (z >= 0) {
		y = y - 1;
		if (y >= 0) {
			z = unknown_int();
		} else {
			z = z - 1;
		}
	}
	return 0;
}