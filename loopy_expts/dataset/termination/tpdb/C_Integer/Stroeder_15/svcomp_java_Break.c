// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_java_Break.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

typedef enum {false, true} bool;

int main() {
    int i;
    int c;
    i = 0;
    c = 0;
    while (i <= 10) {
        i = i + 1;
        c = c + 1;
    }
    return 0;
}