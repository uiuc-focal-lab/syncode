// Source: data/benchmarks/tpdb/C_Integer/Ton_Chanh_15/Singapore_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x;
    int y;
    x = unknown_int();
    y = unknown_int();
    if (x + y <= 0) { 
        while (x > 0) {
            x = x + x + y;
            y = y - 1;
        }
    }
    return 0;
}