// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loops/sum03_true-unreach-call_false-termination.i.annot.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main(){
  int  sn=0;
  unsigned int loop1=unknown_uint(), n1=unknown_uint();
  unsigned int  x=0;
  while(x < 1000000){
    sn = sn +(2);
    x++;
    {;
//@ assert(sn==x*(2)|| sn == 0);
}

  }
}