// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChawdharyCookGulwaniSagivYang-ESOP2008-random1d_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int a = unknown_int();
	int x = unknown_int();
	int max = unknown_int();
	if (max > 0) {
		a = 0;
		x = 1;
		while (x <= max) {
			if (unknown_int())
				a = a + 1;
			else
				a = a - 1;
			x = x + 1;
		}
	}
	return 0;
}