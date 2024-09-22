// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-testloop9_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void errorFn() {ERROR: goto ERROR;}
int main()
{
  int i;
  int x, y;

  i = 0;
  x = 1;

  while (i<10) {
    if (x==1) {
      x = 2;
      y = 3;
    } else if (x==2) {
      x = 3;
      y = 4;
    } else if (x==3) {
      x = 1;
      y = 5;
    } else if (x==4) {
      x = 1;
      y = 6;
    } else {
      x = 2;
    }

    i = i + 1;
  }

  {;
//@ assert(!( y==6 ));
}

}