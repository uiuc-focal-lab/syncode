// Source: data/benchmarks/sv-benchmarks/loop-zilu/benchmark06_conjunctive.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

#include <assert.h>

int main() {
  int j = unknown_int();
  int i = unknown_int();
  int x = unknown_int();
  int y = unknown_int();
  int k = unknown_int();
  j=0;
  if (!(x+y==k)) return 0;
  while (unknown_bool()) {
    if(j==i) {x++;y--;} else {y++;x--;} j++;
  }
  {;
//@ assert(x+y==k);
}

  return 0;
}