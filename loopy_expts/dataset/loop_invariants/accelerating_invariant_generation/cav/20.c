// Source: data/benchmarks/accelerating_invariant_generation/cav/20.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int unknown1(){
    int x; return x;
}
int unknown2();
int unknown3();
int unknown4();

void main()
{
  int x; int y; int k; int j;int i; int n;
    int m = 0;
    if((x+y) != k)
      
return;

    j = 0;
    while(j<=n-1) {
      if(j==i)
      {
         x++;
         y--;
      }else
      {
         y++;
         x--;
      }
	if(unknown1())
  		m = j;
      j++;
    }
    if(j < n)
      
return;

    if(x + y <= k - 1 || x + y >= k + 1 || (n >= 1 && ((m <= -1) || (m >= n))))
    {goto ERROR; { ERROR: {; 
//@ assert(\false);
}
}}
}
