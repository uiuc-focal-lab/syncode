// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/AliasDarteFeautrierGonnord-SAS2010-counterex1a_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int n = unknown_int();
	int b = unknown_int();
	int x = unknown_int();
	int y = unknown_int();
	while (x >= 0 && 0 <= y && y <= n) {
		if (b == 0) {
			y++;
			if (unknown_int())
				b = 1;
		} else {
			y--;
			if (unknown_int()) {
				x--;
				b = 0;
			}
		}
	}
	return 0;
}