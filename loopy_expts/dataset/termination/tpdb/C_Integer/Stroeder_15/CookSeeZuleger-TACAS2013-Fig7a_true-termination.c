// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/CookSeeZuleger-TACAS2013-Fig7a_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, d;
	x = unknown_int();
	y = unknown_int();
	d = unknown_int();
    while (x>0 && y>0 && d>0) {
        if (unknown_int() != 0) {
            x = x - 1;
            d = unknown_int();
        } else {
            x = unknown_int();
            y = y - 1;
            d = d - 1;
        }
    }
    return 0;
}