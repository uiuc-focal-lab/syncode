// Source: data/benchmarks/non_termination/loop/Unsigned_Wraparound_Error_4_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main()
{
    unsigned int n = unknown_uint();
    while( n > 0 )
    {
        unsigned int len = n;
        if( len > 16 )
            len = 16;
        n -= len;
    }
    return 0;
}