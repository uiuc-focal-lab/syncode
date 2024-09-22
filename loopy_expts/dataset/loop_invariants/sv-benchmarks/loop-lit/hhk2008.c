// Source: data/benchmarks/sv-benchmarks/loop-lit/hhk2008.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int a = unknown_int();
    int b = unknown_int();
    int res, cnt;
    if (!(a <= 1000000)) return 0;
    if (!(0 <= b && b <= 1000000)) return 0;
    res = a;
    cnt = b;
    while (cnt > 0) {
	cnt = cnt - 1;
	res = res + 1;
    }
    {;
//@ assert(res == a + b);
}

    return 0;
}