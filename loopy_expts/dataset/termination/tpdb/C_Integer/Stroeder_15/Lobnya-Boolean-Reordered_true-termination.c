// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Lobnya-Boolean-Reordered_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main ()
{
    int x, b;
	x = unknown_int();
	b = unknown_int();
	while (b != 0) {
		b = unknown_int();
		x = x - 1;
        if (x >= 0) {
            b = 1;
        } else {
            b = 0;
        }
	}
	return 0;
}