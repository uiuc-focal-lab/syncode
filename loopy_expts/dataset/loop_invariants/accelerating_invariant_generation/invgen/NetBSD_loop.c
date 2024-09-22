// Source: data/benchmarks/accelerating_invariant_generation/invgen/NetBSD_loop.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int __BLAST_NONDET;

int main ()
{
  
  int MAXPATHLEN;
  int pathbuf_off;

  int bound_off;

  int glob2_p_off;
  int glob2_pathbuf_off;
  int glob2_pathlim_off;

  if(MAXPATHLEN > 0); else goto END;

  pathbuf_off = 0;
  bound_off = pathbuf_off + (MAXPATHLEN + 1) - 1;

  glob2_pathbuf_off = pathbuf_off;
  glob2_pathlim_off = bound_off;

  for (glob2_p_off = glob2_pathbuf_off;
      glob2_p_off <= glob2_pathlim_off;
      glob2_p_off++) {
    
    {;
//@ assert(0 <= glob2_p_off );
}
 {;
//@ assert(glob2_p_off < MAXPATHLEN + 1);
}

  }

 END:  return 0;
}