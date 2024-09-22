// Source: data/benchmarks/accelerating_invariant_generation/svcomp/for_infinite_loop_1_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
  int i=0, x=0, y=0;
  int n=unknown_int();
  assume(n>0);
  for(i=0; 1; i++)
  {
    {;
//@ assert(x==0);
}

  }
  {;
//@ assert(x==0);
}

}
