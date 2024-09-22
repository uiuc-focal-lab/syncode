// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/Masse-VMCAI2014-Fig1b_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	while (x <= 100) {
		if (unknown_int()) {
			x = -2*x + 2;
		} else {
			x = -3*x - 2;
		}
	}
	return 0;
}