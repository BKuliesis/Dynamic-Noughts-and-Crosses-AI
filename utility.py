import random


def random_one_or_zero():
    n = random.randint(0, 1)
    return n


def flip_one_and_zero(n):
    return (n + 1) % 2


def fibonacci(n):
    if n == 1:
        return 0
    elif n == 2:
        return 1
    elif n > 2:
        return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_from_two(n):
    if n == 1:
        return 2
    elif n == 2:
        return 3
    elif n > 2:
        return fibonacci_from_two(n - 1) + fibonacci_from_two(n - 2)


def get_starting_win_length(grid_size):
    temp_size = 2
    n = 1
    while True:
        for size in range(fibonacci_from_two(n)):
            temp_size += 1
            if temp_size == grid_size:
                return grid_size - n + 1
        n += 1


def reverse_merge_sort_tuple(my_list, index):
    if len(my_list) > 1:
        mid = len(my_list) // 2
        left = my_list[:mid]
        right = my_list[mid:]
        # Recursive call on each half
        reverse_merge_sort_tuple(left, index)
        reverse_merge_sort_tuple(right, index)
        # Two iterators for traversing the two halves
        i = j = 0
        # Iterator for the main list
        k = 0
        while i < len(left) and j < len(right):
            if left[i][index] >= right[j][index]:
                # The value from the left half has been used
                my_list[k] = left[i]
                # Move the iterator forward
                i += 1
            else:
                my_list[k] = right[j]
                j += 1
            # Move to the next slot
            k += 1
        # For all the remaining values
        while i < len(left):
            my_list[k] = left[i]
            i += 1
            k += 1
        while j < len(right):
            my_list[k] = right[j]
            j += 1
            k += 1


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
