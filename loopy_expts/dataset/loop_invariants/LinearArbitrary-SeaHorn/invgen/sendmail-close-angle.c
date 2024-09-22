// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/sendmail-close-angle.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

int main (void)
{
  
  int in;
  int inlen = unknown();
  int bufferlen = unknown();
  int buf;
  int buflim;

  if(bufferlen >1);else goto END;
  if(inlen > 0);else goto END;
  if(bufferlen < inlen);else goto END;

  buf = 0;
  in = 0;
  buflim = bufferlen - 2;
    
  while (unknown())
  {
    if (buf == buflim)
      break;
    {;
//@ assert(0<=buf);
}

    {;
//@ assert(buf<bufferlen);
}
 
    buf++;
out:
    in++;
    {;
//@ assert(0<=in);
}

    {;
//@ assert(in<inlen);
}

  }

    {;
//@ assert(0<=buf);
}

    {;
//@ assert(buf<bufferlen);
}

  buf++;

  {;
//@ assert(0<=buf);
}

  {;
//@ assert(buf<bufferlen);
}

  buf++;

 END:  return 0;
}