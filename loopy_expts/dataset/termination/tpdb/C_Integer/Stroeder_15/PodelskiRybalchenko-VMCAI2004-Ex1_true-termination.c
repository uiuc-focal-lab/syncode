// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PodelskiRybalchenko-VMCAI2004-Ex1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int i, j, nondetNat, nondetPos;
	i = unknown_int();
	j = unknown_int();
	while (i - j >= 1) {
        nondetNat = unknown_int();
        if (nondetNat < 0) {
            nondetNat = -nondetNat;
        }
		i = i - nondetNat;
		nondetPos = unknown_int();
        if (nondetPos < 0) {
            nondetPos = -nondetPos;
        }
        nondetPos = nondetPos + 1;
		j = j + nondetPos;
	}
	return 0;
}