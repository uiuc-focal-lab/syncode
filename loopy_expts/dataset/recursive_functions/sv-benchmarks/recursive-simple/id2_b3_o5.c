// Source: data/benchmarks/sv-benchmarks/recursive-simple/id2_b3_o5.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern unsigned int unknown_uint(void);

unsigned int id(unsigned int x);
unsigned int id2(unsigned int x);


/* Function_id */
unsigned int id(unsigned int x) {
  if (x==0) return 0;
  unsigned int ret = id2(x-1) + 1;
  if (ret > 3) return 3;
  return ret;
}


/* Function_id2 */
unsigned int id2(unsigned int x) {
  if (x==0) return 0;
  unsigned int ret = id(x-1) + 1;
  if (ret > 3) return 3;
  return ret;
}


/* Function_main */
int main(void) {
  unsigned int input = unknown_uint();
  unsigned int result = id(input);
  if (result == 5) {
    { ERROR: {; 
//@ assert(\false);
}
}
  }
}