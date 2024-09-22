// Source: data/benchmarks/sv-benchmarks/loops/sum03-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

#include <assert.h>

#define a (2)

int main() { 
  unsigned int sn=0;
  unsigned int loop1=unknown_uint(), n1=unknown_uint();
  unsigned int x=0;

  while(1){
    sn = sn + a;
    x++;
    {;
//@ assert(sn==x*a || sn == 0);
}

  }
}
