def selection_sort(arr: list[float]) -> list[float]:
    """
    使用选择排序算法对数字列表进行排序。

    Args:
        arr: 数字列表。

    Returns:
        排序后的新列表。
    """
    if not isinstance(arr, list) or not all(isinstance(x, (int, float)) for x in arr):
        raise TypeError("输入必须是数字列表")

    sorted_arr = arr.copy()
    n = len(sorted_arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if sorted_arr[j] < sorted_arr[min_idx]:
                min_idx = j
        sorted_arr[i], sorted_arr[min_idx] = sorted_arr[min_idx], sorted_arr[i]
    return sorted_arr
