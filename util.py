import math

def partition_array(array, number_of_partitions):
    partition_size = math.ceil(len(array)/number_of_partitions)
    chunked = []
    for i in range(number_of_partitions):
        if len(array) != 0:
            chunked.append(array[0:partition_size])
            del array[0:partition_size]
    return chunked

def calculate_price_change(final_price:int, original_price:int):
    return (final_price - original_price)/original_price

def check_overlap(phrase, sentence):
    if phrase !=  None and sentence != None:
        phrase_partitioned = phrase.split()

        for phrase in phrase_partitioned:
            for i in range(len(sentence) - 2):
                if len(phrase[i:i+3]) != 3:
                    break
                if phrase[i:i+3] in sentence:
                    return True

    return False

