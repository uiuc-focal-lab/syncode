// Source: data/benchmarks/tpdb/C/AProVE_numeric/svcomp_java_Continue1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
	int i = 0;
    int c = 0;
	while (i < 20) {
	    i++;
	    if (i <= 10) continue;
        c++;
	}
    return c;
}