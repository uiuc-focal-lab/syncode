// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/AliasDarteFeautrierGonnord-SAS2010-speedpldi2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int n = unknown_int();
	int m = unknown_int();
	int v1, v2;
	if (n >= 0 && m > 0) {
		v1 = n;
		v2 = 0;
		while (v1 > 0) {
			if (v2 < m) {
				v2++;
				v1--;
			} else {
				v2 = 0;
			}
		}
	}
	return 0;
}