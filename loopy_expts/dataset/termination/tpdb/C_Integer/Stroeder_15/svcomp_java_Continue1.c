// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_java_Continue1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

typedef enum {false, true} bool;

int main() {
	int i;
    int c;
	i = 0;
    c = 0;
	while (i < 20) {
	    i = i + 1;
	    if (i <= 10) {
        } else {
            c = c + 1;
        }
	}
    return 0;
}