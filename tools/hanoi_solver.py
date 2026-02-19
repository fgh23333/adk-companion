def hanoi_solver(n, source, destination, auxiliary):
    """
    递归解决汉诺塔问题并打印出移动步骤。

    Args:
        n (int): 盘子的数量。
        source (str): 起始柱。
        destination (str): 目标柱。
        auxiliary (str): 辅助柱。
    """
    if n > 0:
        # 将 n-1 个盘子从起始柱移动到辅助柱
        hanoi_solver(n - 1, source, auxiliary, destination)

        # 移动第 n 个盘子到目标柱
        print(f"Move disk {n} from {source} to {destination}")

        # 将 n-1 个盘子从辅助柱移动到目标柱
        hanoi_solver(n - 1, auxiliary, destination, source)

if __name__ == "__main__":
    try:
        num_disks = int(input("请输入汉诺塔的盘子数量: "))
        if num_disks > 0:
            print(f"解决 {num_disks} 个盘子的汉诺塔问题步骤如下:")
            hanoi_solver(num_disks, 'A', 'C', 'B')
        else:
            print("盘子数量必须是正整数。")
    except ValueError:
        print("无效输入，请输入一个整数。")
