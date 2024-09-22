// Source: data/benchmarks/sv-benchmarks/loops/for_infinite_loop_2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
  unsigned int i=0;
  int x=0, y=0;
  int n=unknown_int();
  if (!(n>0)) return 0;
  for(i=0; 1; i++)
  {
    {;
//@ assert(x==0);
}

  }
  {;
//@ assert(x!=0);
}

}
