# Arrays and Strings

The array is the simplest and most important data structure. It stores elements side by side in memory, which makes reading any element by its position instant. Strings are, at heart, arrays of characters. This chapter covers how arrays work, their costs, and the classic techniques used to solve array and string problems: two pointers, sliding windows and prefix sums.

## How Arrays Work

An **array** stores elements of the same type in **contiguous** (adjacent) memory locations. If the array starts at memory address `base` and each element takes `size` bytes, element i lives at:

```
address(i) = base + i * size
```

Because this is simple arithmetic, accessing any element by its **index** takes O(1) time, no matter how large the array is. This is called **random access**.

Indexes usually start at 0, so an array of n elements has indexes 0 to n - 1.

### Static and Dynamic Arrays

- A **static array** has a fixed size chosen when it is created, as in C: `int marks[50];`.
- A **dynamic array** grows automatically. Python's `list`, Java's `ArrayList` and C++'s `vector` are dynamic arrays. When full, they allocate a larger block (often double the size) and copy the elements across, which gives amortised O(1) appends (Chapter 1).

## Costs of Array Operations

| Operation | Time | Why |
|---|---|---|
| Access by index | O(1) | Address arithmetic |
| Update by index | O(1) | Address arithmetic |
| Search (unsorted) | O(n) | May check every element |
| Search (sorted) | O(log n) | Binary search |
| Append at end | O(1) amortised | Occasional resize |
| Insert at position i | O(n) | Shift later elements right |
| Delete at position i | O(n) | Shift later elements left |

> **Key idea:** Arrays are excellent for reading and for adding at the end, but inserting or deleting in the middle is slow, because elements must shift to keep the memory contiguous.

## Traversal and Basic Operations

```python
marks = [72, 85, 91, 64, 88]

total = 0
for m in marks:               # traversal: O(n)
    total += m
average = total / len(marks)

marks.append(79)              # O(1) amortised
marks.insert(0, 50)           # O(n): everything shifts right
marks.pop()                   # O(1): remove last
marks.pop(0)                  # O(n): everything shifts left
```

### Reversing an Array In Place

```python
def reverse(a):
    left, right = 0, len(a) - 1
    while left < right:
        a[left], a[right] = a[right], a[left]
        left += 1
        right -= 1
```

This runs in O(n) time and O(1) extra space. It is also our first example of the **two-pointer technique**.

## Two-Dimensional Arrays

A **2-D array** (matrix) stores data in rows and columns, such as a chessboard, an image or a spreadsheet. In memory it is still one long block. In **row-major order** (used by C and Python's NumPy by default), row 0 comes first, then row 1, and so on:

```
address(r, c) = base + (r * number_of_columns + c) * size
```

Traversing row by row is faster than column by column, because it reads memory in order and uses the CPU cache well.

## Technique 1: Two Pointers

Use two indexes that move through the array according to some rule, often from both ends towards the middle.

**Problem:** in a *sorted* array, find two numbers that add up to a target.

```python
def pair_with_sum(a, target):
    left, right = 0, len(a) - 1
    while left < right:
        s = a[left] + a[right]
        if s == target:
            return left, right
        if s < target:
            left += 1          # need a bigger sum
        else:
            right -= 1         # need a smaller sum
    return None
```

The brute-force approach checks all pairs in O(n^{2}). Two pointers solve it in O(n), because each step rules out an element forever.

Other two-pointer problems include removing duplicates from a sorted array, merging two sorted arrays, and checking whether a string is a palindrome.

## Technique 2: Sliding Window

A **sliding window** is a range [left, right] that moves across the array, growing on one side and shrinking on the other. It turns many O(n^{2}) "check every subarray" problems into O(n).

**Problem:** the maximum sum of any k consecutive elements.

```python
def max_window_sum(a, k):
    window = sum(a[:k])
    best = window
    for right in range(k, len(a)):
        window += a[right] - a[right - k]    # add new element, drop old one
        best = max(best, window)
    return best
```

Instead of re-adding k numbers for every window, we update the sum in O(1) as the window slides.

**Variable-size windows** grow until a condition breaks, then shrink from the left. For example, finding the longest substring without repeating characters:

```python
def longest_unique(s):
    seen = {}
    left = best = 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1            # jump past the previous copy
        seen[ch] = right
        best = max(best, right - left + 1)
    return best
```

## Technique 3: Prefix Sums

A **prefix sum** array stores running totals: prefix[i] is the sum of the first i elements.

```python
def build_prefix(a):
    prefix = [0]
    for x in a:
        prefix.append(prefix[-1] + x)
    return prefix

# sum of a[i..j] inclusive, in O(1):
# prefix[j + 1] - prefix[i]
```

After O(n) preparation, any range sum takes O(1). This is invaluable when there are many range queries on data that does not change.

## Kadane's Algorithm

**Problem:** find the contiguous subarray with the largest sum (the array may contain negatives).

```python
def max_subarray(a):
    best = current = a[0]
    for x in a[1:]:
        current = max(x, current + x)      # extend the run, or start fresh
        best = max(best, current)
    return best
```

At each element we decide whether to extend the current run or start a new one. It runs in O(n) with O(1) space, a classic example of a simple, powerful idea.

## Strings

A **string** is a sequence of characters. In many languages, including Python and Java, strings are **immutable**: they cannot be changed after creation. "Modifying" a string really creates a new one.

> **Key idea:** Building a string by repeated `s = s + piece` in a loop can take O(n^{2}) time, because each step copies the whole string. Collect pieces in a list and use `"".join(pieces)` instead, which is O(n).

### Common String Operations

| Operation | Python | Typical cost |
|---|---|---|
| Length | `len(s)` | O(1) |
| Character at i | `s[i]` | O(1) |
| Substring | `s[i:j]` | O(j - i) |
| Search for pattern | `s.find(p)` | O(n * m) worst case |
| Concatenate | `s + t` | O(len(s) + len(t)) |
| Split / join | `s.split()`, `"".join(parts)` | O(n) |

### Classic String Problems

**Palindrome check** (two pointers):

```python
def is_palindrome(s):
    s = [c.lower() for c in s if c.isalnum()]
    return s == s[::-1]
```

**Anagram check** (counting):

```python
from collections import Counter

def are_anagrams(a, b):
    return Counter(a) == Counter(b)        # "listen" and "silent" -> True
```

Counting characters with a dictionary or a fixed-size array of 26 counts is a pattern that appears in countless string problems.

### Pattern Matching

The naive way to find a pattern of length m in a text of length n tries every starting position: O(n * m) in the worst case. Smarter algorithms such as **KMP** (Knuth-Morris-Pratt) and **Rabin-Karp** achieve roughly O(n + m) by avoiding repeated comparisons. KMP precomputes how far the pattern can safely shift after a mismatch; Rabin-Karp compares hash values of windows before comparing characters.

## Summary

- Arrays store elements contiguously, giving O(1) access by index but O(n) insertion and deletion in the middle.
- Dynamic arrays grow by resizing, with amortised O(1) appends.
- Two pointers, sliding windows and prefix sums turn many O(n^{2}) problems into O(n).
- Kadane's algorithm finds the maximum subarray sum in O(n).
- Strings are often immutable; build them with join, not repeated concatenation.
- Counting characters solves many string problems; KMP and Rabin-Karp speed up pattern matching.

## Practice Questions

1. Why is inserting at the start of an array O(n)?
2. Use two pointers to remove duplicates from a sorted array in place.
3. Find the maximum average of any 4 consecutive elements using a sliding window.
4. Using prefix sums, answer: what is the sum of elements from index 2 to 5 of [3, 1, 4, 1, 5, 9, 2]?
5. Trace Kadane's algorithm on [-2, 1, -3, 4, -1, 2, 1, -5, 4].
