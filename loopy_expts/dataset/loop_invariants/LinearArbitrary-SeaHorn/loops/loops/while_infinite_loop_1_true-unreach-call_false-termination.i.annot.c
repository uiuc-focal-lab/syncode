// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loops/while_infinite_loop_1_true-unreach-call_false-termination.i.annot.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(){
  int  x=0;

  while(1)
  {
    {;
//@ assert(x==0);
}

  }

  {;
//@ assert(x!=0);
}

}