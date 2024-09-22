// Source: data/benchmarks/non_termination/loop/Unsigned_Wraparound_Error_1_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main()
{
    unsigned int best = unknown_uint();
    unsigned int cur = best;
    unsigned int pre;
    unsigned int st_max = unknown_uint();
    unsigned int it_min = unknown_uint();
    if( st_max <= it_min )
        return 0;
    if( best == 0 )
        return 0;
    for( ;  ; )
    {
        if( st_max < cur )
        break;
        pre = cur;
        cur += best;
        if( cur <= pre )
            break;
    }
    return 0;
}