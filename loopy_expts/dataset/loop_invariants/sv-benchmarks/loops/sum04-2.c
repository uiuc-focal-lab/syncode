// Source: data/benchmarks/sv-benchmarks/loops/sum04-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

#include <assert.h>

#define a (2)
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
