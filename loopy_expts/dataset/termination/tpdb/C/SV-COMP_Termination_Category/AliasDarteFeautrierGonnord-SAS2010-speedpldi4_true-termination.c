// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/AliasDarteFeautrierGonnord-SAS2010-speedpldi4_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int n = unknown_int();
	int m = unknown_int();
	int i;
	if (m > 0 && n > m) {
		i = n;
		while (i > 0) {
			if (i < m)
				i--;
			else
				i -= m;
		}
	}
	return 0;
}