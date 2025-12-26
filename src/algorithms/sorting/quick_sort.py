
def quick_sort(arr):
    """
    Sorts an array using the quicksort algorithm.

    Args:
        arr (list): The list of elements to sort.

    Returns:
        list: The sorted list.
    """
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)

# Example usage:
# sorted_array = quick_sort([3, 6, 8, 10, 1, 2, 1])
# print(sorted_array)
