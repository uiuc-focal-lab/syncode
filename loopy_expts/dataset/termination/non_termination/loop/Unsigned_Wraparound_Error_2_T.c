// Source: data/benchmarks/non_termination/loop/Unsigned_Wraparound_Error_2_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main()
{
    unsigned int ui = 1;
    unsigned int size = unknown_uint();
    unsigned int BUFFSIZE = unknown_uint();
    if( size < BUFFSIZE )
        size = BUFFSIZE;
    while( (ui < size) && ( ui * 2 > ui ) )
        ui *= 2;
    return 0;
}