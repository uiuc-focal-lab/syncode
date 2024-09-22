// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaC9.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int x;
    int y;
    int random;
    x = unknown_int();
    y = unknown_int();
    
    while (x > 0 && y > 0) {
        random = unknown_int();
        if (random < 42) {
            x = x-1;
            random = unknown_int();
            y = random;
        } else {
            y = y-1;
        }
    }
    
    return 0;
}