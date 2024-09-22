// Source: data/benchmarks/non_termination/loop/Using_Erroneous_Condition_2_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
    int reg_count = unknown_int();
    if( reg_count > 65534)
        return 0;
    for( int i = 0 ; i < reg_count ; i++ )
    {
        
    }
    return 0;
}