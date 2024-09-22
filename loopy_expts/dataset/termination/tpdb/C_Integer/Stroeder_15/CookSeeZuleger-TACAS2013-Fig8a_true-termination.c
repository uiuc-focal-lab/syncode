// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/CookSeeZuleger-TACAS2013-Fig8a_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x;
	x = unknown_int();
	while (x != 0) {
		if (x > 0) {
			x = x - 1;
		} else {
			x = x + 1;
		}
	}
	return 0;
}