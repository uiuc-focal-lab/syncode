// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PlusSwap.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int x;
    int y;
    int z;
    int res;
    x = unknown_int();
    y = unknown_int();
    res = 0;
    
    while (y > 0) {
        z = x;
        x = y-1;
        y = z;
        res = res+1;
    }
    
    res = res + x;
    
    return 0;
}