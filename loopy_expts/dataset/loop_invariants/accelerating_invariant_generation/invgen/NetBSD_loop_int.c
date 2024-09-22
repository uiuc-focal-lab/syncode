// Source: data/benchmarks/accelerating_invariant_generation/invgen/NetBSD_loop_int.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int __BLAST_NONDET;
int MAXPATHLEN;

int main ()
{
  
  int buf_off;
  int pattern_off;
  int bound_off;

  int glob3_pathbuf_off;
  int glob3_pathend_off;
  int glob3_pathlim_off;
  int glob3_pattern_off;
  int glob3_dc;

  if(MAXPATHLEN > 0); else goto END;

  buf_off = 0;
  pattern_off = 0;

  bound_off = 0 + (MAXPATHLEN + 1) - 1;

  glob3_pathbuf_off = buf_off;
  glob3_pathend_off = buf_off;
  glob3_pathlim_off = bound_off;
  glob3_pattern_off = pattern_off;

  glob3_dc = 0;
  for (;;)
    if (glob3_pathend_off + glob3_dc >= glob3_pathlim_off) break;
    else {
      
      glob3_dc++;
      
      {;
//@ assert(0 <= glob3_dc);
}
{;
//@ assert(glob3_dc < MAXPATHLEN + 1);
}

      if (__BLAST_NONDET) goto END;
    }

 END:  return 0;
}