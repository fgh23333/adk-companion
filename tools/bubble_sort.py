def bubble_sort(arr: list[int | float]) -> list[int | float]:
    """
    使用冒泡排序算法对数字列表进行排序。

    Args:
        arr: 一个包含整数或浮点数的列表。

    Returns:
        一个包含已排序元素的新列表。
    """
    n = len(arr)
    # 创建一个副本以避免修改原始列表
    new_arr = arr[:]
    # 遍历所有数组元素
    for i in range(n):
        # 最后的 i 个元素已经就位
        for j in range(0, n-i-1):
            # 从 0 到 n-i-1 遍历数组
            # 如果发现元素大于下一个元素，则交换
            if new_arr[j] > new_arr[j+1]:
                new_arr[j], new_arr[j+1] = new_arr[j+1], new_arr[j]
    return new_arr