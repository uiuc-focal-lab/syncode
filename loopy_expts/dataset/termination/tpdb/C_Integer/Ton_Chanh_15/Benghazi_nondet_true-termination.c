// Source: data/benchmarks/tpdb/C_Integer/Ton_Chanh_15/Benghazi_nondet_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x, d1, d2, d1old;
    x = unknown_int();
    d1 = unknown_int();
    d2 = unknown_int();
	while (x >= 0) {
		x = x - d1;
		d1old = d1;
		d1 = d2 + 1;
		d2 = d1old + 1;
	}
	return 0;
}