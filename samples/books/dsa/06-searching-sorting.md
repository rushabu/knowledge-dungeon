# Searching and Sorting

Searching and sorting are the bread and butter of computing. Every time you look up a contact, filter products by price or see a leaderboard, some searching or sorting algorithm is at work. This chapter covers linear and binary search, the simple quadratic sorts, the efficient O(n log n) sorts, and sorts that beat O(n log n) by avoiding comparisons.

## Linear Search

Check each element in turn until you find the target.

```python
def linear_search(a, target):
    for i, x in enumerate(a):
        if x == target:
            return i
    return -1
```

Time O(n), space O(1). It works on any list, sorted or not, and is the right choice for small or unsorted data.

## Binary Search

If the array is **sorted**, we can do far better. Compare the target with the middle element; if the target is smaller, it can only be in the left half, otherwise the right half. Each step halves the search space.

```python
def binary_search(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

Time **O(log n)**: a million sorted items need at most about 20 comparisons.

> **Key idea:** Binary search is famous for off-by-one bugs. Decide whether your range is inclusive [lo, hi] or half-open [lo, hi), and keep the loop condition and updates consistent with that choice.

### Variations

- **First or last occurrence** of a repeated value: when you find a match, record it and keep searching to the left (or right).
- **Lower bound:** the first index whose value is >= target. It is the position where the target would be inserted. Python's `bisect_left` does this.
- **Binary search on the answer:** when a yes/no condition changes only once as a number increases ("can we finish all tasks in X hours?"), binary search over X instead of over an array.

## Properties of Sorting Algorithms

- **Time complexity** (best, average, worst).
- **Space:** **in-place** algorithms use O(1) or O(log n) extra memory.
- **Stability:** a **stable** sort keeps equal elements in their original relative order. If students are already sorted by name and you then stably sort by marks, students with equal marks stay alphabetical.
- **Adaptivity:** runs faster on nearly sorted input.

## Simple Quadratic Sorts

These are easy to understand and fine for tiny arrays, but O(n^{2}) makes them impractical for large data.

### Bubble Sort

Repeatedly swap adjacent elements that are out of order. After each pass, the largest remaining element "bubbles" to the end.

```python
def bubble_sort(a):
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:          # already sorted: stop early
            break
```

Worst O(n^{2}), best O(n) with the early exit. Stable and in place.

### Selection Sort

Find the smallest element and swap it into the first position; then the smallest of the rest into the second position; and so on. Always O(n^{2}) comparisons, but at most n - 1 swaps, which helps when writing to memory is expensive. Not stable.

### Insertion Sort

Build a sorted section at the front. Take each new element and slide it left into its correct place, like sorting a hand of playing cards.

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
```

Worst O(n^{2}), but **O(n) on nearly sorted data**. It is stable, in place and very fast for small arrays, which is why real-world sorts switch to insertion sort for tiny pieces.

## Merge Sort

**Merge sort** is divide and conquer:

1. Split the array into two halves.
2. Recursively sort each half.
3. **Merge** the two sorted halves into one sorted array.

```python
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:            # <= keeps it stable
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    return merged + left[i:] + right[j:]
```

The array is halved log n times, and each level of merging does O(n) work, so merge sort is **O(n log n) in every case**. It is **stable** but needs **O(n) extra space**. It is also ideal for linked lists and for **external sorting** of data too large for memory.

## Quick Sort

**Quick sort** is also divide and conquer, but the hard work happens *before* the recursion:

1. Pick a **pivot** element.
2. **Partition** the array so that elements smaller than the pivot come before it and larger ones after it. The pivot is now in its final position.
3. Recursively sort the two sides.

```python
def quick_sort(a, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    if lo < hi:
        p = partition(a, lo, hi)
        quick_sort(a, lo, p - 1)
        quick_sort(a, p + 1, hi)

def partition(a, lo, hi):          # Lomuto scheme, last element as pivot
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i
```

- **Average case:** O(n log n), with small constants, so it is often the fastest sort in practice.
- **Worst case:** O(n^{2}), when the pivot is always the smallest or largest element, for example choosing the last element of an already sorted array.
- In place (O(log n) stack space on average), but **not stable**.

> **Key idea:** Choosing the pivot at random, or as the median of the first, middle and last elements, makes the worst case extremely unlikely.

## Heap Sort

**Heap sort** builds a max-heap (Chapter 8) from the array, then repeatedly swaps the maximum to the end and restores the heap. It is O(n log n) in every case and in place, but not stable, and it is usually slower in practice than quick sort because of poor cache behaviour.

## Comparing the Main Sorts

| Algorithm | Best | Average | Worst | Space | Stable |
|---|---|---|---|---|---|
| Bubble | O(n) | O(n^{2}) | O(n^{2}) | O(1) | Yes |
| Selection | O(n^{2}) | O(n^{2}) | O(n^{2}) | O(1) | No |
| Insertion | O(n) | O(n^{2}) | O(n^{2}) | O(1) | Yes |
| Merge | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick | O(n log n) | O(n log n) | O(n^{2}) | O(log n) | No |
| Heap | O(n log n) | O(n log n) | O(n log n) | O(1) | No |

### The Comparison Lower Bound

Any sort that works only by comparing pairs of elements needs **at least O(n log n)** comparisons in the worst case. There are n! possible orderings, and each comparison at best halves the possibilities, so about log_{2}(n!) comparisons, roughly n log n, are needed. Merge sort and heap sort are therefore optimal among comparison sorts.

## Non-Comparison Sorts

If we know more about the keys, we can beat n log n.

### Counting Sort

For integers in a small range 0 to k, count how many times each value occurs, then write them out in order. Time O(n + k). Excellent for marks out of 100 or ages, useless if k is huge.

### Radix Sort

Sort numbers digit by digit, from the least significant digit to the most, using a stable counting sort for each digit. Time O(d x (n + b)) for d digits in base b. It is great for fixed-length keys such as phone numbers or IDs.

### Bucket Sort

Spread values that are uniformly distributed (say between 0 and 1) into n buckets, sort each small bucket, and concatenate. Average O(n).

## Sorting in Real Life

Library sorts are hybrids tuned for real data:

- **Timsort** (Python's `sorted` and Java's object sort) combines merge sort and insertion sort, detects already sorted runs, and is stable. It is O(n) on sorted data and O(n log n) in the worst case.
- **Introsort** (C++ `std::sort`) starts with quick sort, switches to heap sort if the recursion gets too deep, and uses insertion sort for small pieces.

```python
students = [("Riya", 88), ("Arjun", 92), ("Meera", 88)]
students.sort(key=lambda s: s[1], reverse=True)     # stable: Riya stays before Meera
```

## Summary

- Linear search is O(n) on any data; binary search is O(log n) on sorted data.
- Binary search extends to first/last occurrence, lower bounds and searching over answers.
- Bubble, selection and insertion sort are O(n^{2}); insertion sort is excellent on small or nearly sorted data.
- Merge sort is a stable, guaranteed O(n log n) sort using O(n) space; quick sort is usually fastest but has an O(n^{2}) worst case.
- Comparison sorts cannot beat O(n log n); counting, radix and bucket sort can when keys are suitable.
- Real libraries use hybrids like Timsort and Introsort.

## Practice Questions

1. Trace binary search for 23 in [2, 5, 8, 12, 16, 23, 38, 56, 72, 91].
2. What does it mean for a sort to be stable? Give a situation where stability matters.
3. Show the passes of insertion sort on [5, 2, 4, 6, 1, 3].
4. Why does quick sort degrade to O(n^{2}) on a sorted array with the last element as pivot? How do you prevent it?
5. When would counting sort be a poor choice?
