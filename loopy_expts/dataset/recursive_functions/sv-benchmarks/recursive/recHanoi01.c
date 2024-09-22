// Source: data/benchmarks/sv-benchmarks/recursive/recHanoi01.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);

int counter;


/* Function_hanoi */
int hanoi(int n) {
	if (n == 1) {
		return 1;
	}
	return 2 * (hanoi(n-1)) + 1;
}


/* Function_applyHanoi */
void applyHanoi(int n, int from, int to, int via)
{
	if (n == 0) {
		return;
	}
	
	counter++;
	applyHanoi(n-1, from, via, to);
	applyHanoi(n-1, via, to, from);
}


/* Function_main */
int main() {
    int n = unknown_int();
    if (n < 1 || n > 31) {
    	return 0;
    }
    counter = 0;
    applyHanoi(n, 1, 3, 2);
    int result = hanoi(n);
    
    if (result == counter) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}
