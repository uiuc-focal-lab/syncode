// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/AliasDarteFeautrierGonnord-SAS2010-cousot9_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int j = unknown_int();
	int N = unknown_int();
	int i = N;
	while (i > 0) {
		if (j > 0) {
			j--;
		} else {
			j = N;
			i--;
		}
	}
	return 0;
}