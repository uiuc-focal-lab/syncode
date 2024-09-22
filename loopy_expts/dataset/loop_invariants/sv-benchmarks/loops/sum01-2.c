// Source: data/benchmarks/sv-benchmarks/loops/sum01-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

#define a (2)

int main() { 
  int i, n=unknown_int(), sn=0;
  if (!(n < 1000 && n >= -1000)) return 0;
  for(i=1; i<=n; i++) {
    sn = sn + a;
  }
  {;
//@ assert(sn==n*a || sn == 0);
}

}