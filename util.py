import math

def partition_array(array, number_of_partitions):
    partition_size = math.ceil(len(array)/number_of_partitions)
    chunked = []
    for i in range(number_of_partitions):
        if len(array) != 0:
            chunked.append(array[0:partition_size])
            del array[0:partition_size]
    return chunked

