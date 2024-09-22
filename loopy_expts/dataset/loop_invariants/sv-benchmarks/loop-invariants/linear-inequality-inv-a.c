// Source: data/benchmarks/sv-benchmarks/loop-invariants/linear-inequality-inv-a.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned char unknown_uchar(void);

int main() {
  unsigned char n = unknown_uchar();
  if (n == 0) {
    return 0;
  }
  unsigned char v = 0;
  unsigned int  s = 0;
  unsigned int  i = 0;
  while (i < n) {
    v = unknown_uchar();
    s += v;
    ++i;
  }
  if (s < v) {
    {; 
//@ assert(\false);
};
    return 1;
  }
  if (s > 65025) {
    {; 
//@ assert(\false);
};
    return 1;
  }
  return 0;
}