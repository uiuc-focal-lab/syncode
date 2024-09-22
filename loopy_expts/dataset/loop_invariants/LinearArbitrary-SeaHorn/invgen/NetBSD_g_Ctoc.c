// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/NetBSD_g_Ctoc.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

int main ()
{
  int BASE_SZ = unknown();
  int __BLAST_NONDET = unknown();
  
  int i;
  int j;
  int len = BASE_SZ;

  if(BASE_SZ > 0 ); else goto END;

  {;
//@ assert( 0 <= BASE_SZ-1 );
}

  if (len == 0)
    goto END; 
  
  i = 0;
  j = 0;
  while (1) {
    if ( len == 0 ){ 
      goto END;
    } else {
      {;
//@ assert( 0<= j );
}
 {;
//@ assert(j < BASE_SZ);
}

      {;
//@ assert( 0<= i );
}
 {;
//@ assert(i < BASE_SZ );
}

      if ( __BLAST_NONDET ) {
        i++;
        j++;
        goto END;
      }
    }
    i ++;
    j ++;
    len --;
  }

 END:  return 0;
}
