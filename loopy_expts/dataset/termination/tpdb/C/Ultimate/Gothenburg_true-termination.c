// Source: data/benchmarks/tpdb/C/Ultimate/Gothenburg_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	int a = unknown_int();
	int b = unknown_int();
	int x = unknown_int();
	int y = unknown_int();
	if (a != b) {
		return 0;
	}
	while (x >= 0 || y >= 0) {
		x = x + a - b - 1;
		y = y + b - a - 1;
	}
	return 0;
}