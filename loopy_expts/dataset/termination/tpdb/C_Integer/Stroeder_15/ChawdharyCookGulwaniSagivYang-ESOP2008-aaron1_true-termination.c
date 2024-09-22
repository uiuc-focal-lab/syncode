// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChawdharyCookGulwaniSagivYang-ESOP2008-aaron1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int i, j, an, bn;
	i = unknown_int();
	j = unknown_int();
	an = unknown_int();
	bn = unknown_int();
	while ((an >= i && bn >= j) || (an >= i && bn <= j) || (an <= i && bn >= j)) {
		if (an >= i && bn >= j) {
			if (unknown_int() != 0) {
				j = j + 1;
			} else {
				i = i + 1;
			}
		} else {if (an >= i && bn <= j) {
			i = i + 1;
		} else {if (an <= i && bn >= j) {
			j = j + 1;
		}}}
	}
	return 0;
}