// Source: data/benchmarks/tpdb/C/Ultimate/Stockholm_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	int x = unknown_int();
	int a = unknown_int();
	int b = unknown_int();
	if (a != b) {
		return 0;
	}
	while (x >= 0) {
		x = x + a - b - 1;
	}
	return 0;
}