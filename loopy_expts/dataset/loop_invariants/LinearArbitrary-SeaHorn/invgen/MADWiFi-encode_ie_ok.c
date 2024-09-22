// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/MADWiFi-encode_ie_ok.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

int main()
{
  
  int p;
  int i;
  int leader_len = unknown();
  int bufsize = unknown();
  int bufsize_0 = unknown();
  int ielen = unknown();

  if(leader_len >0); else goto END;
  if(bufsize >0); else goto END;
  if(ielen >0); else goto END;

  if (bufsize < leader_len)
    goto END;

  p = 0;
  
  bufsize_0 = bufsize;
  bufsize -= leader_len;
  p += leader_len;

  if (bufsize < 2*ielen)
    goto END;

  for (i = 0; i < ielen && bufsize > 2; i++) {
    {;
//@ assert(0<=p);
}

    {;
//@ assert(p+1<bufsize_0);
}

    p += 2;
  }

 END:;
}
