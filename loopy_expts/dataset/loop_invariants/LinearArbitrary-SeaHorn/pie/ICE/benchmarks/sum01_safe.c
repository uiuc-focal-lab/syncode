// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/sum01_safe.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() { 
  int i, n=unknown_int(), sn=0;
  for(i=1; i<=n; i++) {
    sn = sn + 1;
  }
  {;
//@ assert(sn==n || sn == 0);
}

}