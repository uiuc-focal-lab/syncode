// Source: data/benchmarks/sv-benchmarks/recursive-simple/id_b3_o5-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_id */
int id(int x) {
  if (x==0) return 0;
  int ret = id((unsigned int)x-1) + 1;
  if (ret > 3) return 3;
  return ret;
}


/* Function_main */
int main(void) {
  int input = unknown_int();
  int result = id(input);
  if (result == 5) {
    { ERROR: {; 
//@ assert(\false);
}
}
  }
}