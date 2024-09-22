// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/sum03_safe.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main() { 
  int sn=0;
  unsigned int loop1=unknown_uint(), n1=unknown_uint();
  unsigned int x=0;

  while(1){
    sn = sn + 1;
    x++;
    {;
//@ assert(sn==x*1 || sn == 0);
}

  }
}
