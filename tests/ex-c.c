#include <stdio.h>

int main() {
    //REPOBEE-SANITIZER-START
    int x = 42;
    printf("%d\n", x);
    //REPOBEE-SANITIZER-REPLACE-WITH
    ////TODO: To be completed
    //int x = 0;
    //REPOBEE-SANITIZER-END

    return 0;
}
