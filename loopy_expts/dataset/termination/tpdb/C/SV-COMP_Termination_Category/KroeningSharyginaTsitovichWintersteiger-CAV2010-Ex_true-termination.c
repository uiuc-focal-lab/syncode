// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/KroeningSharyginaTsitovichWintersteiger-CAV2010-Ex_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int i = unknown_int();
	while (i < 255) {
		if (unknown_int()) {
			i = i + 1;
		} else {
			i = i + 2;
		}
	}
	return 0;
}