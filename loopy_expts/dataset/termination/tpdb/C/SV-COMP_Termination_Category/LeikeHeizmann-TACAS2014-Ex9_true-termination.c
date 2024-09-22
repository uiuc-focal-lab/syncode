// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/LeikeHeizmann-TACAS2014-Ex9_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int q = unknown_int();
	int p = unknown_int();
	while (q > 0 && p > 0) {
		if (q < p) {
			q = q - 1;
		} else {
			if (p < q) {
				p = p - 1;
			} else {
				break;
			}
		}
	}
	return 0;
}