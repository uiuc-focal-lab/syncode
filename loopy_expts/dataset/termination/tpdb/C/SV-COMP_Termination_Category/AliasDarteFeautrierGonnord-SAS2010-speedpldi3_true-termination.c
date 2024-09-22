// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/AliasDarteFeautrierGonnord-SAS2010-speedpldi3_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int n = unknown_int();
	int m = unknown_int();
	int i, j;
	if (m > 0 && n > m) {
		i = 0;
		j = 0;
		while (i < n) {
			if (j < m) {
				j++;
			} else {
				j = 0;
				i++;
			}
		}
	}
	return 0;
}