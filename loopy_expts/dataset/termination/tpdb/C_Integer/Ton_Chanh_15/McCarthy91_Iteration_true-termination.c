// Source: data/benchmarks/tpdb/C_Integer/Ton_Chanh_15/McCarthy91_Iteration_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
  int c, n;
  c = 1;
  n = unknown_int();
  while (c > 0) {
    if (n > 100) {
      n = n - 10;
      c = c - 1;
    } else {
      n = n + 11;
      c = c + 1;
    }
  }
  return 0;
}