// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/MinusMin.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int x;
    int y;
    int res;
    int min;
    x = unknown_int();
    y = unknown_int();
    res = 0;
    
    if (x < y) { min = x; }
    else { min = y; }
    
    while (min == y) {
        y = y+1;
        res = res+1;
        if (x < y) { min = x; }
        else { min = y; }
    }
    
    return 0;
}