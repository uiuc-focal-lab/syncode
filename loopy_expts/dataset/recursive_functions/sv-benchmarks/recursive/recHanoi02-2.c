// Source: data/benchmarks/sv-benchmarks/recursive/recHanoi02-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_hanoi */
int hanoi(int n) {
    if (n == 1) {
		return 1;
	}
	return 2 * (hanoi(n-1)) + 1;
}


/* Function_main */
int main() {
    int n = unknown_int();
    if (n < 1 || n > 31) {
    	return 0;
    }
    int result = hanoi(n);
    if (result >= 0) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}
