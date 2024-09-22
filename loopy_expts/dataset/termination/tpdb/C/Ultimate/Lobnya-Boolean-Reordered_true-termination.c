// Source: data/benchmarks/tpdb/C/Ultimate/Lobnya-Boolean-Reordered_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main ()
{
	int x = unknown_int();
	int b = unknown_int();
	while (1) {
		if (!b) {
			break;
		}
		b = unknown_int();
		x = x - 1;
		b = (x >= 0);
	}
	return 0;
}