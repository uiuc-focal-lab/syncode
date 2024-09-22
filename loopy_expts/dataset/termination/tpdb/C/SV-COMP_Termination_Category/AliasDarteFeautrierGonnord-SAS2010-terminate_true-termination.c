// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/AliasDarteFeautrierGonnord-SAS2010-terminate_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int i = unknown_int();
	int j = unknown_int();
	int k = unknown_int();
	int ell;
	while (i <= 100 && j <= k) {
		ell = i;
		i = j;
		j = ell + 1;
		k--;
	}
	return 0;
}