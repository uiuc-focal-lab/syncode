// Source: data/benchmarks/accelerating_invariant_generation/cav/37.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int unknown1(){
    int x; return x;
}

int unknown2();
int unknown3();
int unknown4();

void main() {
  int x= 0;
  int m=0;
  int n = unknown1();
  while(x<=n-1) {
     if(unknown1()) {
	m = x;
     }
     x= x+1;
  }
  if(x < n)
    
return;

  if(n>=1 && (m <= -1 || m >= n))
  {goto ERROR; { ERROR: {; 
//@ assert(\false);
}
}}

}