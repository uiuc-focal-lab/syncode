#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main()
{
  unsigned int n = unknown_uint();
  unsigned int  x=n,  y=0;
  while(x>0)
  {
    x--;
    y++;
  }
  {;
//@ assert(y==n);
}

}