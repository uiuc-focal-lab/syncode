// Source: data/benchmarks/non_termination/loop/Undefined_Behavior_3_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main()
{
    unsigned int val = unknown_uint();
    int bytes = 1;
    while( val >> bytes * 8 && bytes < 4 )
        bytes++;
    return 0;
}