// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-rsd_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int r, da, db, temp;
	r = unknown_int();
	if (r >= 0) {
		da = 2 * r;
		db = 2 * r;
		while (da >= r) {
			if (unknown_int() != 0) {
				da = da - 1;
			} else {
				temp = da;
				da = db - 1;
				db = da;
			}
		}
	}
	return 0;
}