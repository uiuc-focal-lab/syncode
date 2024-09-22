// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/MirrorInterv.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int i;
    int range;
    i = unknown_int();
    range = 20;
    
    while (-range <= i && i <= range) {
        if (range-i < 5 || range+i < 5) {
            i = i*(-1);
        } else {
            range = range+1;
            i = i-1;
            if (i == 0) {
                range = -1;
            }
        }
    }
    
    return 0;
}