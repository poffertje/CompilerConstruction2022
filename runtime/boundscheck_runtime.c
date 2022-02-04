#include <stdio.h>
#include <stdlib.h>

void __coco_check_bounds(long offset, long array_size) {
    if (offset >= array_size || offset < 0) {
        fprintf(stderr, "Array access out of bounds. offset: %ld, array_size: %ld\n", offset, array_size);
        exit(1);
    }
}
