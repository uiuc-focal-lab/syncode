// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/LeikeHeizmann-WST2014-Ex9_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	while (x > 0) {
		x = x / 2;
	}
	return 0;
}