# Algorithms and Complexity

A **data structure** is a way of organising data so that it can be used efficiently. An **algorithm** is a finite, step-by-step procedure for solving a problem. Together they are the heart of programming: the right data structure makes an algorithm simple, and the right algorithm makes a program fast. This chapter explains how we measure "fast" and "memory-hungry" in a way that does not depend on any particular computer.

## What Makes a Good Algorithm?

An algorithm should be:

- **Correct:** it produces the right output for every valid input.
- **Finite:** it always finishes.
- **Definite:** every step is precise and unambiguous.
- **Efficient:** it uses as little time and memory as reasonably possible.

Correctness comes first. A fast algorithm that gives wrong answers is useless. But among correct algorithms, efficiency often decides whether a program finishes in a second or in a week.

## Why Not Just Time It?

We could run two programs and use a stopwatch, but the result depends on the computer, the language, the compiler, other running programs and the particular input. We need a measure that describes how the running time **grows as the input grows**. That measure is **asymptotic complexity**.

## Counting Steps

Consider finding the largest number in a list.

```python
def find_max(nums):
    best = nums[0]            # 1 step
    for x in nums:            # n iterations
        if x > best:          # 1 comparison each
            best = x          # at most 1 assignment each
    return best               # 1 step
```

For a list of n numbers, this does roughly 2n + 2 basic steps. As n becomes large, the constants 2 and +2 stop mattering. What matters is that the work grows **in proportion to n**. We say the algorithm runs in **O(n)** time, read "order n" or "big-O of n".

## Big-O, Big-Omega and Big-Theta

- **Big-O (O)** gives an **upper bound**: the algorithm grows *no faster than* this. f(n) = O(g(n)) if f(n) <= c * g(n) for some constant c and all large enough n.
- **Big-Omega** gives a **lower bound**: the algorithm grows *at least* this fast.
- **Big-Theta** gives a **tight bound**: both upper and lower, so the growth rate is exactly this.

In everyday use, people say "big-O" and usually mean the tight bound for the worst case.

### Rules for Simplifying

1. **Drop constants:** O(3n) becomes O(n); O(n / 2) becomes O(n).
2. **Keep only the dominant term:** O(n^{2} + 5n + 100) becomes O(n^{2}), because for large n the n^{2} term swamps the rest.
3. **Different inputs get different variables:** looping over list A and then list B is O(a + b), not O(n).

## Common Complexity Classes

| Big-O | Name | Example | n = 1,000,000 needs about |
|---|---|---|---|
| O(1) | Constant | Access an array element by index | 1 step |
| O(log n) | Logarithmic | Binary search | 20 steps |
| O(n) | Linear | Scan a list once | 1 million steps |
| O(n log n) | Linearithmic | Merge sort | 20 million steps |
| O(n^{2}) | Quadratic | Compare every pair | 10^{12} steps |
| O(2^{n}) | Exponential | Try every subset | Impossible |
| O(n!) | Factorial | Try every ordering | Impossible |

> **Key idea:** A computer doing around a hundred million simple steps per second finishes an O(n log n) job on a million items instantly, but an O(n^{2}) job takes hours. Choosing a better complexity class beats buying a faster computer.

### Why log n Is So Small

log_{2}(n) asks "how many times can I halve n before reaching 1?" Halving a million takes only about 20 steps; halving a billion takes about 30. Any algorithm that throws away half the remaining problem at each step, such as binary search, runs in O(log n).

## Analysing Loops

- A single loop over n items: **O(n)**.
- Two nested loops, each over n items: **O(n^{2})**.

```python
for i in range(n):
    for j in range(n):
        print(i, j)           # runs n * n times
```

- Nested loops where the inner loop shrinks:

```python
for i in range(n):
    for j in range(i + 1, n):
        compare(i, j)          # runs n(n-1)/2 times, still O(n^2)
```

- A loop that doubles or halves its counter: **O(log n)**.

```python
i = 1
while i < n:
    i *= 2                     # runs about log2(n) times
```

- Consecutive (not nested) loops add up: O(n) + O(n) = O(n).

## Best, Worst and Average Case

The same algorithm can behave differently on different inputs of the same size. Consider searching a list for a value from the start:

- **Best case:** the value is first. O(1).
- **Worst case:** the value is last or absent. O(n).
- **Average case:** on average we look through half the list. O(n).

We usually quote the **worst case**, because it is a guarantee: the algorithm will never be slower than this.

## Space Complexity

**Space complexity** measures the extra memory an algorithm needs as a function of input size. `find_max` uses only a couple of variables, so it needs O(1) extra space. An algorithm that copies the input into a new list uses O(n). Recursive algorithms also use stack space for each pending call (Chapter 5).

There is often a **time-space trade-off**: using extra memory, such as a hash table, can make an algorithm much faster.

## Amortised Analysis

Some operations are usually cheap but occasionally expensive. Appending to a Python list is normally O(1), but when the underlying array is full, the list allocates a bigger array and copies everything, which is O(n). Because the array doubles in size each time, these expensive copies are rare. Averaged over many appends, each append costs O(1). This average over a sequence of operations is called **amortised** complexity.

## A Worked Comparison: Checking for Duplicates

Problem: does a list contain any duplicate values?

**Approach 1: compare every pair.**

```python
def has_duplicate_slow(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False
```

Time O(n^{2}), space O(1).

**Approach 2: sort first.** Duplicates end up next to each other.

```python
def has_duplicate_sort(nums):
    nums = sorted(nums)
    return any(nums[i] == nums[i + 1] for i in range(len(nums) - 1))
```

Time O(n log n), space O(n) for the sorted copy.

**Approach 3: use a set.**

```python
def has_duplicate_fast(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
```

Time O(n) on average, space O(n). This is the time-space trade-off in action: extra memory buys a big speed-up.

## Abstract Data Types

An **abstract data type (ADT)** describes *what* operations a structure supports, not *how* they are implemented. A **stack** ADT promises push, pop and peek. It could be implemented with an array or a linked list. Separating the interface from the implementation lets us change the implementation without changing the programs that use it.

The rest of this book studies the most important data structures (arrays, linked lists, stacks, queues, trees, heaps, hash tables and graphs) and the algorithms that go with them.

## Summary

- Algorithms must be correct, finite, definite and efficient.
- Asymptotic complexity describes how time or memory grows with input size, independent of hardware.
- Big-O is an upper bound; drop constants and lower-order terms.
- Common classes, from fastest to slowest: O(1), O(log n), O(n), O(n log n), O(n^{2}), O(2^{n}), O(n!).
- Nested loops multiply; consecutive loops add; halving loops give O(log n).
- Worst-case analysis gives guarantees; amortised analysis averages over sequences of operations.
- Extra memory can often buy speed.

## Practice Questions

1. Simplify: O(5n^{2} + 3n log n + 20).
2. What is the time complexity of a loop that runs while i < n, with i starting at n and being halved each time?
3. Give an example of an algorithm whose best and worst cases differ.
4. Explain amortised O(1) append with an example.
5. Write an O(n) algorithm to find whether two numbers in a list add up to a target value.
