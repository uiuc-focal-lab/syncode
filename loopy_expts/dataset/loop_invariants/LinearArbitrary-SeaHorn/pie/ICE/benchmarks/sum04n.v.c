// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/sum04n.v.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#define a (1)

int main() { 
  int i, sn=0;
  int SIZE = unknown_int();
  int v1, v2, v3;
  for(i=1; i<=SIZE; i++) {
    sn = sn + a;
    v1 = unknown_int();
    v2 = unknown_int();
    v3 = unknown_int();
  }
  {;
//@ assert(sn==SIZE*a || sn == 0);
}

}
