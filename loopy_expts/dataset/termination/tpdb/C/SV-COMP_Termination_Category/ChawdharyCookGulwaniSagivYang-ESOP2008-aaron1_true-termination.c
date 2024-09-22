// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChawdharyCookGulwaniSagivYang-ESOP2008-aaron1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int i = unknown_int();
	int j = unknown_int();
	int an = unknown_int();
	int bn = unknown_int();
	while ((an >= i && bn >= j) || (an >= i && bn <= j) || (an <= i && bn >= j)) {
		if (an >= i && bn >= j) {
			if (unknown_int()) {
				j = j + 1;
			} else {
				i = i + 1;
			}
		} else if (an >= i && bn <= j) {
			i = i + 1;
		} else if (an <= i && bn >= j) {
			j = j + 1;
		}
	}
	return 0;
}