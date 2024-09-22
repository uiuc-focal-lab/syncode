// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loops/for_infinite_loop_1_true-unreach-call_false-termination.i.annot.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main(){
  unsigned int i=0;
  int  x=0,  y=0;
  int  n=unknown_int();
assume(n>0);
  for(i=0; 1; i++)
  {
    {;
//@ assert(x==0);
}

  }
  {;
//@ assert(x==0);
}

}