// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/HeizmannHoenickeLeikePodelski-ATVA2013-Fig2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int y = unknown_int();
	int x = y + 42;
	while (x >= 0) {
		y = 2*y - x;
		x = (y + x) / 2;
	}
	return 0;
}