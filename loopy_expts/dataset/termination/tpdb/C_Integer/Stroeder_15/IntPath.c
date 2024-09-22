// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/IntPath.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int i;
    int x;
    int y;
    i = unknown_int();
    x = 0;
    y = 0;
    
    if (i > 10) {
        x = 1;
    } else {
        y = 1;
    }
    while (x == y) { }
    
    return 0;
}