// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/sum04.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

#define a (1)
#define SIZE 8
int main() { 
  int i, sn=0;
  for(i=1; i<=SIZE; i++) {
    sn = sn + a;
  }
  {;
//@ assert(sn==SIZE*a || sn == 0);
}

}
