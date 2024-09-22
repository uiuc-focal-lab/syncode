// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loops/trex03_true-unreach-call.i.annot.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);
extern _Bool unknown_bool(void);

int main()
{
  unsigned int  x1=unknown_uint(),  x2=unknown_uint(),  x3=unknown_uint();
  unsigned int  d1=1,  d2=1,  d3=1;
  int  c1=unknown_bool(),  c2=unknown_bool();
  while(x1>0 && x2>0 && x3>0)
  {
    if(c1)x1=x1-d1;
    else if(c2)x2=x2-d2;
    else x3=x3-d3;
    c1=unknown_bool();
    c2=unknown_bool();
  }
  {;
//@ assert(x1==0 || x2==0 || x3==0);
}

  return 0;
}