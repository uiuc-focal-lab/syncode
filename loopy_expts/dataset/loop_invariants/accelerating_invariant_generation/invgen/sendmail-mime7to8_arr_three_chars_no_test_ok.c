// Source: data/benchmarks/accelerating_invariant_generation/invgen/sendmail-mime7to8_arr_three_chars_no_test_ok.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main (void)
{
  
  int __BLAST_NONDET;
  int fbuflen;
  int fb;
  
  if(fbuflen >0);else goto END;
  fb = 0;
  while (__BLAST_NONDET)
  {
    
    if (__BLAST_NONDET)
      break;

    if (__BLAST_NONDET)
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