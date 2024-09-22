// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/CookSeeZuleger-TACAS2013-Fig7b_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, z;
	x = unknown_int();
	y = unknown_int();
	z = unknown_int();
	while (x>0 && y>0 && z>0) {
		if (unknown_int() != 0) {
			x = x - 1;
		} else {if (unknown_int() != 0) {
			y = y - 1;
			z = unknown_int();
		} else {
			z = z - 1;
			x = unknown_int();
		}}
	}
    return 0;
}