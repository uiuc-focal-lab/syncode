// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Piecewise_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int p, q;
	q = unknown_int();
	p = unknown_int();
	while (q > 0 && p > 0 && p != q) {
		if (q < p) {
			q = q - 1;
			p = unknown_int();
		} else {if (p < q) {
			p = p - 1;
			q = unknown_int();
		}}
	}
	return 0;
}