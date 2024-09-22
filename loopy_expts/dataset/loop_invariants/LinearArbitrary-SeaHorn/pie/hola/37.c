// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/37.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();
extern int unknown2();

void main() {
  int x= 0;
  int m=0;
  int n = unknown1();
  while(x<n) {
     if(unknown2()) {
	m = x;
     }
     x= x+1;
  }
  if(n>0) {;
//@ assert(0<=m && m<n);
}

}