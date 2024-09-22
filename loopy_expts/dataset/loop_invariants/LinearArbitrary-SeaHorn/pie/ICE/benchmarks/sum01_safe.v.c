// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/sum01_safe.v.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() { 
  int i, n=unknown_int(), sn=0, v1,v2,v3;
  for(i=1; i<=n; i++) {
    sn = sn + 1;
    v1 = unknown_int();
    v2 = unknown_int();
    v3 = unknown_int();
  }
  {;
//@ assert(sn==n || sn == 0);
}

}