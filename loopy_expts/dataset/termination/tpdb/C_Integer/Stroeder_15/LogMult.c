// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/LogMult.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int x;
    int y;
    int res;
    x = unknown_int();
    y = 2;
    res = 1;
    
    if (x < 0 || y < 1) { }
    else {
        while (x > y) {
            y = y*y;
            res = 2*res;
        }
    }
    
    return 0;
}