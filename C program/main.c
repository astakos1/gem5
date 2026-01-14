#include <stdio.h>

#define n 100

int main() {
    int i;
    long long sum = 0;


    printf("Selected integer: 100");
    

    for (i = 1; i <= n; ++i) {
        sum += i;
    }

    printf("The sum of numbers from 1 to 100 is: %lld\n", sum);

    return 0;
}