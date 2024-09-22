// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/AliasDarteFeautrierGonnord-SAS2010-rsd_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int r = unknown_int();
	int da, db, temp;
	if (r >= 0) {
		da = 2 * r;
		db = 2 * r;
		while (da >= r) {
			if (unknown_int()) {
				da--;
			} else {
				temp = da;
				da = db - 1;
				db = da;
			}
		}
	}
	return 0;
}