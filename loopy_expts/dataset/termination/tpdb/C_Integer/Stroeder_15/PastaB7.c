// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaB7.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int x;
    int y;
    int z;
    x = unknown_int();
    y = unknown_int();
    z = unknown_int();
    
    while (x > z && y > z) {
        x = x-1;
        y = y-1;
    }
    
    return 0;
}