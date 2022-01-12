#include <stdio.h>

void __coco_dummy_print_allocation(int elems) {
    printf("Allocating %d elements on stack\n", elems);
}
