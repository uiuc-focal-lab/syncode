// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/BradleyMannaSipma-ICALP2005-Fig1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	int y = unknown_int();
	int N = unknown_int();
	
	if (N >= 536870912 || x >= 536870912 || y >= 536870912 || x < -1073741824) {
		return 0;
	}
	if (x + y >= 0) {
		while (x <= N) {
			if (unknown_int()) {
				x = 2*x + y;
				y = y + 1;
			} else {
				x = x + 1;
			}
		}
	}
	return 0;
}
