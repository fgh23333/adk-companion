def fibonacci_sum(n):
    """
    Calculates the sum of the Fibonacci sequence up to the n-th term.

    Args:
        n: The number of terms (integer >= 0).

    Returns:
        The sum of the first n Fibonacci numbers.
        Returns 0 if n is negative.
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    a, b = 0, 1
    total_sum = 1
    for _ in range(2, n + 1):
        a, b = b, a + b
        total_sum += b
    
    return total_sum

if __name__ == '__main__':
    num_terms = 10
    print(f"The sum of the first {num_terms} terms of the Fibonacci sequence is: {fibonacci_sum(num_terms)}")
