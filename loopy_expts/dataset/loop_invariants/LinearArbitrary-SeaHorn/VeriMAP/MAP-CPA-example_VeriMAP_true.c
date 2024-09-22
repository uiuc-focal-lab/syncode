// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/MAP-CPA-example_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  int i = 0;
  int a = 0;

  while (1) {
    if (i == 20) {
       goto LOOPEND;
    } else {
       i++;
       a++;
    }

    if (i != a) {
      goto ERROR;
    }
  }

  LOOPEND:

  if (a != 20) {
     goto ERROR;
  }

  return (0);
  { ERROR: {; 
//@ assert(\false);
}
}
  return (-1);
}
