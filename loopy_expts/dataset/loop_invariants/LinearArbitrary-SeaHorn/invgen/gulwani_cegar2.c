#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

void main() {
  int x,m,n;
  n = unknown();
  x = 0;
  m = 0;
  while( x < n ) {
    if(unknown())
	m = x;
	x++;
  }
  if( n > 0 )
    {
      {;
//@ assert( 0<=m);
}

      {;
//@ assert(m<n);
}

    }
}