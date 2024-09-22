// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Stockholm_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x;
    int a;
    int b;
    x = unknown_int();
    a = unknown_int();
    b = unknown_int();
    if (a == b) {
        while (x >= 0) {
            x = x + a - b - 1;
        }
    }
    return 0;
}