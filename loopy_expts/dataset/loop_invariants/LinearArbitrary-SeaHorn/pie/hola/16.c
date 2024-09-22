// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/16.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();

int main() {

  int i = unknown1();
  int j = unknown1();
  
  int x = i;
  int y = j;
 
  while(x!=0) {
	x--;
	y--;
  }
  if(i==j)
	{;
//@ assert(y==0);
}

}
