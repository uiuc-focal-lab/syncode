// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/CookSeeZuleger-TACAS2013-Fig8a-modified_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int K, x;
    K = unknown_int();
    x = unknown_int();
    while (x != K) {
        if (x > K) {
            x = x - 1;
        } else {
            x = x + 1;
        }
    }
    return 0;
}