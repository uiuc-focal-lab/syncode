// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ComplInterv.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int i;
    i = unknown_int();
    
    while (i*i > 9) {
        if (i < 0) {
            i = i-1;
        } else {
            i = i+1;
        }
    }
	
    return 0;
}