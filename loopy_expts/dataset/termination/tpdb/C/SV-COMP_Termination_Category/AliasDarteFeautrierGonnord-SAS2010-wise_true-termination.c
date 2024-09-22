// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/AliasDarteFeautrierGonnord-SAS2010-wise_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	int y = unknown_int();
	if (x >= 0 && y >= 0) {
		while (x - y > 2 || y - x > 2) {
			if (x < y) {
				x++;
			} else {
				y++;
			}
		}
	}
	return 0;
}