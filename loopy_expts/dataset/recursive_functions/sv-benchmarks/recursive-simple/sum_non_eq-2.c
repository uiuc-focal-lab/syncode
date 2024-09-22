// Source: data/benchmarks/sv-benchmarks/recursive-simple/sum_non_eq-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern unsigned int unknown_uint(void);


/* Function_sum */
unsigned int sum(unsigned int n, unsigned int m) {
    if (n == 0) {
      return m;
    } else {
      return sum(n - 1, m + 1);
    }
}


/* Function_main */
int main(void) {
  unsigned int a = unknown_uint();
  unsigned int b = unknown_uint();
  unsigned int result = sum(a, b);
  if (result != a + b) {
    { ERROR: {; 
//@ assert(\false);
}
}
  }
}