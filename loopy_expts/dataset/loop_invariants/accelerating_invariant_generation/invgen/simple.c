#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void main() {
  int x=0;
  int n;
  
  assume(n > 0 );
  while( x < n ){
    x++;
  }
  {;
//@ assert( x<=n );
}

}