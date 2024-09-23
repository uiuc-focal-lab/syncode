#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void main() {
  int i;
  int j;
  int x = i;
  int y = j;
  while(x!=0) {
	x--;
	y--;
  }
  if(i==j)
	if(y != 0) {;
//@ assert(0);
}

}