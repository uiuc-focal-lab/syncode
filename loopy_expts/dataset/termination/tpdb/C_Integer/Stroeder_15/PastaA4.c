// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaA4.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int x;
    int y;
    x = unknown_int();
    y = unknown_int();
    
    while (x > y) {
        y = y+1;
    }
    
    return 0;
}