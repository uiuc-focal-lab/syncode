#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int SIZE = 40000; 

int main() {
  int i;
  unsigned long long sum;
  i = 0, sum =0; 
  while(i< SIZE){ 
      i = i + 1; 
      sum += i;
  }
  {;
//@ assert( sum == ((SIZE *(SIZE+1))/2));
}

  return 0;
}