// Source: data/benchmarks/LinearArbitrary-SeaHorn/invgen/sendmail-mime-fromqp.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

extern int unknown();

int main (void)
{
  int outfilelen = unknown();
  
  int nchar = 0;

  int out = 0; 

  if(outfilelen > 0); else goto RETURN;

  while(unknown())
  {
    
    if(unknown())
    {
      
      if(unknown())
	
	goto AFTERLOOP; 

      if(unknown())
      {
	out = 0;
	nchar = 0;
	goto LOOPEND;
      }
      else
      {
	
	if(unknown())  goto AFTERLOOP;

	nchar++;
	if (nchar >= outfilelen)
	  goto AFTERLOOP;

	{;
//@ assert(0<=out);
}

	{;
//@ assert(out<outfilelen);
}

	out++;
      }
    }
    else
    {
      
      nchar++;
      if (nchar >= outfilelen)
	goto AFTERLOOP;

      {;
//@ assert(0<=out);
}

      {;
//@ assert(out<outfilelen);
}

      out++;

      if(unknown()) goto AFTERLOOP;
    }
  LOOPEND:;
  }
 AFTERLOOP:

  {;
//@ assert(0<=out);
}

  {;
//@ assert(out<outfilelen);
}

  out++;
 RETURN:  return 0;
}