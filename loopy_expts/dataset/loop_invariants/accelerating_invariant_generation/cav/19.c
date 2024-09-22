// Source: data/benchmarks/accelerating_invariant_generation/cav/19.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int unknown1(){
    int x; return x;
}

int unknown2(){
    int x; return x;
}

int unknown3();
int unknown4();

int n, m;

void main()
{
  n = unknown1();
  m = unknown2();
  int x=0; 
  int y;
  y = m;
  if(n < 0)
    
return;

  if(m < 0)
    
return;

  if(m > n-1)
    
return;

  while(x<=n-1) {
    x++;
    if(x>=m+1) y++;
    else if(x > m) 
return;

    x = x;
  }
  if(x < n)
    
return;

  if(y >= n+1)
  {goto ERROR; { ERROR: {; 
//@ assert(\false);
}
}}
}