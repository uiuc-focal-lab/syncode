// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/DivMinus.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int x;
    int y;
    int res;
    x = unknown_int();
    y = unknown_int();
    res = 0;
    
    while (x >= y && y > 0) {
      x = x-y;
      res = res + 1;
    }
    
    return 0;
}