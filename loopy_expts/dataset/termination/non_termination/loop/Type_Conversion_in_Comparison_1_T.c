// Source: data/benchmarks/non_termination/loop/Type_Conversion_in_Comparison_1_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern unsigned short unknown_ushort(void);

int main()
{
    unsigned short int s, seqnum;
    int len;
    seqnum = unknown_ushort();
    len = unknown_int();
    int i;
    for( i = 0, s = seqnum ; i < len; i++, s++ )
    {

    }
    return 0;
}