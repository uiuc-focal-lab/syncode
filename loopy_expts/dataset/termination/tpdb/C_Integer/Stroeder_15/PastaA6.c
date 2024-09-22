// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaA6.c
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
    
    while (x > y + z) {
        y = y+1;
        z = z+1;
    }
    
    return 0;
}