// Source: data/benchmarks/accelerating_invariant_generation/svcomp/sum01_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#define a (2)

int main() { 
  int i, n=unknown_int(), sn=0;
  for(i=1; i<=n; i++) {
    sn = sn + a;
  }
  {;
//@ assert(sn==n*a || sn == 0);
}

}