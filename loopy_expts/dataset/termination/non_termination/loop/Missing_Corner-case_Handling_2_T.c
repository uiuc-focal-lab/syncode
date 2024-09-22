// Source: data/benchmarks/non_termination/loop/Missing_Corner-case_Handling_2_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
    int val = unknown_int();
    if( val <= 0  )
        return 0;
    int bits;
    for( bits = 0 ; val != 0 ; bits++ )
        val >>= 1;
    return 0;
}