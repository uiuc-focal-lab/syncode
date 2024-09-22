// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/KroeningSharyginaTsitovichWintersteiger-CAV2010-Ex_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int i;
	i = unknown_int();
	while (i < 255) {
		if (unknown_int() != 0) {
			i = i + 1;
		} else {
			i = i + 2;
		}
	}
	return 0;
}