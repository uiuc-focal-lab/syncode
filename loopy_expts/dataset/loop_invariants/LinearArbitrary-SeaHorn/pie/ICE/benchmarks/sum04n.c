// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/sum04n.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#define a (1)

int main() { 
  int i, sn=0;
  int SIZE = unknown_int();
  for(i=1; i<=SIZE; i++) {
    sn = sn + a;
  }
  {;
//@ assert(sn==SIZE*a || sn == 0);
}

}
