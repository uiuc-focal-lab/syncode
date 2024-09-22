// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark03_linear.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int x = unknown_int();
  int y = unknown_int();
  int i = unknown_int();
  int j = unknown_int();
  
  _Bool flag = unknown_bool();
  x = 0; y = 0;
  if (!(i==0 && j==0)) return 0;
  while (unknown_bool()) {
    x++;
    y++;
    i+=x;
    j+=y;
    if (flag) j+=1;
  }
  {;
//@ assert(j>=i);
}

  return 0;
}