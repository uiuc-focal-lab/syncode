// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_easySum.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
  int i, sum, bound;
  bound = unknown_int();
  i = 0;
  sum = 0;
  while (i<bound) {
    sum = sum + i;
    i = i + 1;
  }
  return 0;
}