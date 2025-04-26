#include <stdio.h>
#include <stdlib.h>

int main() {
    int *numbers;
    int i, n;

    printf("Enter number of elements: ");
    scanf("%d", &n);

    numbers = NULL;

    for (i = 0; i <= n; i++) {
        printf("Enter number %d: ", i+1);
        scanf("%d", &numbers[i]);
    }

    printf("You entered:\n");
    for (i = 0; i <= n; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\n");

    for (i = 0; i < n; i++) {
        for (int j = i; j < n; j++) {
            if (numbers[i] > numbers[j]) {
                int temp = numbers[i];
                numbers[i] = numbers[j];
                numbers[j] = temp
            }
        }
    }

    printf("Sorted numbers:\n");
    for (i = 0; i <= n; i++) {
        printf("%d ", numbers[i]);
    }

    return 0;
}