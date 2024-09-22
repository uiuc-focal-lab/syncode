// Source: data/benchmarks/sv-benchmarks/loop-lit/ddlm2013.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    unsigned int i,j,a,b;
    int flag = unknown_int();
    a = 0;
    b = 0;
    j = 1;
    if (flag) {
        i = 0;
    } else {
        i = 1;
    }

    while (unknown_int()) {
        a++;
        b += (j - i);
        i += 2;
        if (i%2 == 0) {
            j += 2;
        } else {
            j++;
        }
    }
    if (flag) {
        {;
//@ assert(a == b);
}

    }
    return 0;
}