// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Nyala-2lex_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
	int x, y;
	while (x >= 0 && y >= 0) {
		y = y - 1;
		if (y < 0) {
			x = x - 1;
			y = unknown_int();
		}
	}
    return 0;
}