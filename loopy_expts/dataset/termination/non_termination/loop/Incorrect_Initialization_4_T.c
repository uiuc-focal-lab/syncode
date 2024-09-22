// Source: data/benchmarks/non_termination/loop/Incorrect_Initialization_4_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
    int h = unknown_int();
    int hash = unknown_int();
    int rehash = unknown_int();
    if( h < 0 || hash <= 0 || rehash <= 0 || rehash > hash || hash > 65534)
        return 0;
    int i = h % hash;
    int r = 0;
    while( i < hash )
    {
        if( !r ) r = ( h % rehash ) + 1;
        i += r;
    }
    return 0;
}