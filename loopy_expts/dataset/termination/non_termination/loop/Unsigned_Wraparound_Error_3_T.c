// Source: data/benchmarks/non_termination/loop/Unsigned_Wraparound_Error_3_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main()
{
    unsigned int pathlen = unknown_uint();
    unsigned int newbufsize = unknown_uint();
    unsigned int len = unknown_uint();
    if( newbufsize + len + 1 == 0xffffffff )
        return 0;
    if( newbufsize == 0 )
        return 0;
    while( newbufsize < pathlen + len + 1 )
    {
        if( newbufsize >= 0x80000000 )
            newbufsize = 0xffffffff;
        else
            newbufsize *= 2;
    }
    return 0;
}