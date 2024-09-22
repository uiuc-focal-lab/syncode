// Source: data/benchmarks/non_termination/loop/Incorrect_Update_for_Loop_Iterator_1_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
    int max_msg_size = unknown_int();
    int buffer_read_offset = unknown_int();
    int buffer_bytes_left = unknown_int();
    if( max_msg_size < -1 || buffer_read_offset <= 0 || buffer_bytes_left < 0 )
        return 0;
    int size = 64;
    while( buffer_bytes_left < size / 2)
    {
        size *= 2;
        if( max_msg_size != -1 && size > max_msg_size )
        {
            size = max_msg_size;
            break;
        }
        buffer_bytes_left = size - buffer_bytes_left;
    }
    return 0;
}