// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/CookSeeZuleger-TACAS2013-Fig7b_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	int y = unknown_int();
	int z = unknown_int();
	while (x>0 && y>0 && z>0) {
		if (unknown_int()) {
			x = x - 1;
		} else if (unknown_int()) {
			y = y - 1;
			z = unknown_int();
		} else {
			z = z - 1;
			x = unknown_int();
		}
	}
}