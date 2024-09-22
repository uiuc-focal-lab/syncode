// Source: data/benchmarks/tpdb/C/Ultimate/Nyala-2lex_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x, y;
	while (x >= 0) {
		y = y - 1;
		if (y < 0) {
			x = x - 1;
			y = unknown_int();
		}
		if (y < 0) {
			break;
		}
	}
}