// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/McCarthyIterative.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int x;
    int c;
    x = unknown_int();
    c = 1;
    
    while (c > 0) {
        if (x > 100) {
            x = x-10;
            c = c-1;
        } else {
            x = x+11;
            c = c+1;
        }
    }
    
    return 0;
}