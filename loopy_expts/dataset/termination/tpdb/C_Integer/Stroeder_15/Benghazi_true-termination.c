// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Benghazi_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x, d1, d2, d1old;
	d1 = 73;
	d2 = 74;
	x = unknown_int();
	while (x >= 0) {
		x = x - d1;
		d1old = d1;
		d1 = d2 + 1;
		d2 = d1old + 1;
	}
	return 0;
}