def insertion_sort(arr: list[float]) -> list[float]:
    """
    使用插入排序算法对数字列表进行排序。

    Args:
        arr: 数字列表。

    Returns:
        排序后的新列表。
    """
    if not isinstance(arr, list) or not all(isinstance(x, (int, float)) for x in arr):
        raise TypeError(\"输入必须是数字列表\")

    sorted_arr = arr.copy()
    for i in range(1, len(sorted_arr)):
        key = sorted_arr[i]
        j = i - 1
        while j >= 0 and key < sorted_arr[j]:
            sorted_arr[j + 1] = sorted_arr[j]
            j -= 1
        sorted_arr[j + 1] = key
    return sorted_arr
