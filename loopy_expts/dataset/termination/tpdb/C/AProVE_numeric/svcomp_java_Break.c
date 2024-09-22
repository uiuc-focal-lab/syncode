// Source: data/benchmarks/tpdb/C/AProVE_numeric/svcomp_java_Break.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
    int i = 0;
    int c = 0;
    while (1) {
        if (i > 10) break;
        i++;
        c++;
    }
    return c;
}