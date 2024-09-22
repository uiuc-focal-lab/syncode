// Source: data/benchmarks/sv-benchmarks/loops/while_infinite_loop_2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  int x=0;

  while(1)
  {
    {;
//@ assert(x==0);
}
    
  }

  {;
//@ assert(x==0);
}

}