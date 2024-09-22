// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/sendmail-mime7to8_arr_three_chars_no_test_ok.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

int main (void)
{
  
  int fbuflen = unknown();
  int fb;
  
  if(fbuflen >0);else goto END;
  fb = 0;
  while (unknown())
  {
    
    if (unknown())
      break;

    if (unknown())
      break;

    {;
//@ assert(0<=fb);
}

    {;
//@ assert(fb<fbuflen);
}

    fb++;
    if (fb >= fbuflen-1)
      fb = 0;

    {;
//@ assert(0<=fb);
}

    {;
//@ assert(fb<fbuflen);
}

    fb++;
    if (fb >= fbuflen-1)
      fb = 0;

    {;
//@ assert(0<=fb);
}

    {;
//@ assert(fb<fbuflen);
}

    fb++;
    if (fb >= fbuflen-1)
      fb = 0;
  }

  if (fb > 0)
  {
    
    {;
//@ assert(0<=fb);
}

    {;
//@ assert(fb<fbuflen);
}

  }

 END:  return 0;
}