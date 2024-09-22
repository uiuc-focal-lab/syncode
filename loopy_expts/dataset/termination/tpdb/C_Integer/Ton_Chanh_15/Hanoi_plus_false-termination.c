// Source: data/benchmarks/tpdb/C_Integer/Ton_Chanh_15/Hanoi_plus_false-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x, y, z;
    x = unknown_int();
    y = unknown_int();
    z = unknown_int();
    while (x > 0) {
        x = x + y;
        y = y + z;
        z = z + x;
    }
    return 0;
}