// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/min_rf_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x,y;
    int z;
   
    x = unknown_int();
    y = unknown_int();
   
    while (y > 0 && x > 0) {
      if (x>y) {
          z = y;
      } else {
          z = x;
      }
      if (unknown_int() != 0) {
          y = y+x;
          x = z-1;
          z = y+z;
      } else {
          x = y+x;
          y = z-1;
          z = x+z;
      }
    }
    return 0;
}