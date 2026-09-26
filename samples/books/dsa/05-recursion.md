# Recursion and Backtracking

A function that calls itself sounds like a trick, but recursion is one of the most natural ways to solve problems that contain smaller copies of themselves. Folders contain folders, trees contain subtrees, and sorting a list can mean sorting two halves. This chapter explains how recursion works, how to write it correctly, and how **backtracking** uses recursion to explore choices systematically.

## The Idea

A **recursive** function solves a problem by:

1. handling a **base case**, a version small enough to answer directly, and
2. reducing larger inputs to **smaller instances of the same problem**, solving those recursively, and combining the results.

The classic example is the factorial: n! = n x (n - 1)!, with 0! = 1.

```python
def factorial(n):
    if n == 0:                 # base case
        return 1
    return n * factorial(n - 1)  # recursive case
```

> **Key idea:** Every recursive call must move closer to a base case. Without a base case, or without progress towards it, the function calls itself forever.

## How Recursion Runs: The Call Stack

Each call gets its own **stack frame** holding its parameters and local variables. Calls pile up until a base case is reached, then return one by one.

```
factorial(3)
  = 3 * factorial(2)
        = 2 * factorial(1)
              = 1 * factorial(0)
                    = 1
              = 1
        = 2
  = 6
```

At the deepest point, four frames are on the stack. The recursion uses O(n) stack space. If the depth is too large, the program crashes with a **stack overflow**. Python's default limit is about 1,000 frames.

## Thinking Recursively

A reliable way to design recursive functions is the "leap of faith":

1. **Define** exactly what the function returns for an input.
2. **Assume** it already works correctly for smaller inputs.
3. **Use** that assumption to solve the current input.
4. **Handle** the base case(s).

Example: the sum of a list.

```python
def total(nums):
    if not nums:
        return 0
    return nums[0] + total(nums[1:])   # first element + sum of the rest
```

(Slicing copies the list, so this particular version is O(n^{2}); passing an index instead avoids the copies. It is shown here for clarity.)

### Reversing a String

```python
def reverse(s):
    if len(s) <= 1:
        return s
    return reverse(s[1:]) + s[0]
```

### Power in O(log n)

Computing x^{n} by multiplying n times is O(n). Recursion does better by halving:

```python
def power(x, n):
    if n == 0:
        return 1
    half = power(x, n // 2)
    return half * half if n % 2 == 0 else half * half * x
```

Each call halves n, so it takes O(log n) multiplications. This is **fast exponentiation**.

## Recurrence Relations

The running time of a recursive function can be written as a **recurrence**:

- factorial: T(n) = T(n - 1) + O(1), giving O(n).
- binary search: T(n) = T(n / 2) + O(1), giving O(log n).
- merge sort: T(n) = 2T(n / 2) + O(n), giving O(n log n).

The **Master Theorem** solves recurrences of the form T(n) = aT(n / b) + O(n^{d}) by comparing d with log_{b}(a):

- if d > log_{b}(a): O(n^{d})
- if d = log_{b}(a): O(n^{d} log n)
- if d < log_{b}(a): O(n^{log_b a})

For merge sort, a = 2, b = 2 and d = 1, so d = log_{2}(2) = 1, which gives O(n log n).

## The Danger of Repeated Work

The Fibonacci sequence is 0, 1, 1, 2, 3, 5, 8, ... where each number is the sum of the previous two.

```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

This is correct but terribly slow. fib(5) calls fib(4) and fib(3); fib(4) calls fib(3) again, and so on. The number of calls grows roughly as O(2^{n}). fib(50) would take hours.

The fix is **memoization**: remember answers you have already computed.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

Now each value is computed once: O(n) time. This idea grows into **dynamic programming** in Chapter 10.

## Types of Recursion

- **Linear recursion:** one recursive call per invocation (factorial).
- **Tree recursion:** several calls per invocation (naive Fibonacci), which often explodes in cost.
- **Tail recursion:** the recursive call is the very last action, so the frame could be reused. Some languages optimise this into a loop; Python does not.
- **Indirect recursion:** A calls B, which calls A.

## Recursion vs Iteration

Anything recursive can be written with loops and an explicit stack, and vice versa.

| | Recursion | Iteration |
|---|---|---|
| Readability | Natural for trees and divide-and-conquer | Natural for simple repetition |
| Memory | Uses call-stack frames | Usually constant extra memory |
| Risk | Stack overflow on deep inputs | Infinite loops |
| Speed | Function-call overhead | Usually slightly faster |

Use recursion where it makes the solution clearer, especially for trees, graphs and divide-and-conquer, and prefer loops for simple linear repetition.

## Divide and Conquer

**Divide and conquer** splits a problem into independent subproblems, solves them recursively, and combines the results.

1. **Divide** the input into smaller parts.
2. **Conquer** each part recursively.
3. **Combine** the partial answers.

Merge sort and quick sort (Chapter 6) and binary search are the classic examples.

## Backtracking

**Backtracking** builds a solution step by step, and **undoes** (backtracks) a choice as soon as it cannot lead to a valid solution. It explores a tree of choices depth-first.

The general pattern:

```python
def backtrack(state):
    if is_solution(state):
        record(state)
        return
    for choice in choices(state):
        if is_valid(state, choice):
            make(state, choice)
            backtrack(state)
            undo(state, choice)       # the "backtrack" step
```

### Example: All Subsets

```python
def subsets(nums):
    result, current = [], []
    def go(i):
        if i == len(nums):
            result.append(current[:])
            return
        current.append(nums[i])      # choose nums[i]
        go(i + 1)
        current.pop()                # un-choose it
        go(i + 1)
    go(0)
    return result

subsets([1, 2, 3])   # 8 subsets
```

There are 2^{n} subsets, so any algorithm that lists them all takes at least O(2^{n}) time.

### Example: Permutations

```python
def permutations(nums):
    result = []
    def go(current, remaining):
        if not remaining:
            result.append(current)
            return
        for i in range(len(remaining)):
            go(current + [remaining[i]], remaining[:i] + remaining[i + 1:])
    go([], nums)
    return result
```

There are n! permutations.

### Example: N-Queens

Place N queens on an N x N chessboard so that no two attack each other. Place one queen per row; for each row, try each column; skip columns and diagonals that are already attacked; if a row has no safe column, backtrack to the previous row and move that queen.

> **Key idea:** Backtracking's power comes from **pruning**: abandoning a partial solution the moment it breaks a rule, which skips huge parts of the search tree.

Sudoku solvers, crossword fillers and maze solvers all use backtracking.

## Summary

- Recursion solves a problem through smaller instances of itself, with a base case to stop.
- Each call uses a stack frame; deep recursion can overflow the stack.
- Design recursively with the leap of faith: define, assume, use, handle the base case.
- Recurrences describe recursive running times; the Master Theorem solves common ones.
- Tree recursion can repeat work exponentially; memoization fixes it.
- Divide and conquer splits, solves and combines; backtracking explores choices and undoes bad ones, pruning early.

## Practice Questions

1. Write a recursive function to count the digits in a positive integer.
2. Draw the call tree of the naive fib(5). How many calls are made?
3. Use the Master Theorem to solve T(n) = 4T(n / 2) + O(n).
4. Write a backtracking function that prints all binary strings of length n with no two consecutive 1s.
5. Explain how pruning makes backtracking faster than brute force, using N-Queens.
