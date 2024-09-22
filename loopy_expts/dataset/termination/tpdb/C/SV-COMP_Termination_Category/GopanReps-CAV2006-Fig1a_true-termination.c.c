// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/GopanReps-CAV2006-Fig1a_true-termination.c.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
	int x = 0, y = 0;
	while (1) {
		if (x <= 50) {
			y++;
		} else {
			y--;
		}
		if (y < 0) {
			break;
		}
		x++;
	}
	return 0;
}