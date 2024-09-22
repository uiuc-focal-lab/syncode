// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChawdharyCookGulwaniSagivYang-ESOP2008-aaron4_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int i, j, k, an, bn, tk;
	i = unknown_int();
	j = unknown_int();
	k = unknown_int();
	an = unknown_int();
	bn = unknown_int();
	tk = unknown_int();
	while (((an >= i && bn >= j) || (an >= i && bn <= j) || (an <= i && bn >= j)) && k >= tk + 1) {
		if (an >= i && bn >= j) {
			if (unknown_int() != 0) {
				j = j + k;
				tk = k;
				k = unknown_int();
			} else {
				i = i + 1;
			}
		} else {if (an >= i && bn <= j) {
			i = i + 1;
		} else {if (an <= i && bn >= j) {
			j = j + k;
			tk = k;
			k = unknown_int();
		}}}
	}
	return 0;
}