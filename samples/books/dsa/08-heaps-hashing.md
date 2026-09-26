# Heaps and Hash Tables

This chapter covers two structures that appear everywhere in practice. A **heap** always gives you the smallest (or largest) element quickly, which makes it the natural home for priority queues. A **hash table** finds, inserts and deletes items by key in expected constant time, making it perhaps the single most useful data structure in everyday programming.

## Heaps

A **binary heap** is a **complete binary tree** (every level full except possibly the last, which fills from the left) that satisfies the **heap property**:

- In a **min-heap**, every node is smaller than or equal to its children, so the minimum is at the root.
- In a **max-heap**, every node is greater than or equal to its children, so the maximum is at the root.

A heap is *not* sorted. It only guarantees that each parent beats its children, which is exactly enough to find the extreme element instantly.

### Storing a Heap in an Array

Because the tree is complete, it can be stored in an array with no pointers at all. For the node at index i (0-based):

```
left child  = 2i + 1
right child = 2i + 2
parent      = (i - 1) // 2
```

The min-heap below is stored as [1, 3, 6, 5, 9, 8]:

```
        1
      /   \
     3     6
    / \   /
   5   9 8
```

> **Key idea:** The complete-tree shape guarantees a height of about log n, and the array layout means no pointer overhead. Both make heaps fast and compact.

### Insertion: Sift Up

1. Place the new element at the end of the array (the next free spot in the bottom level).
2. While it is smaller than its parent (in a min-heap), swap it with the parent.

This takes O(log n), because the element rises at most the height of the tree.

### Removing the Minimum: Sift Down

1. The minimum is at the root. Save it.
2. Move the last element to the root.
3. While it is larger than its smaller child, swap it with that child.

Also O(log n).

```python
def sift_down(heap, i):
    n = len(heap)
    while True:
        smallest, l, r = i, 2 * i + 1, 2 * i + 2
        if l < n and heap[l] < heap[smallest]:
            smallest = l
        if r < n and heap[r] < heap[smallest]:
            smallest = r
        if smallest == i:
            return
        heap[i], heap[smallest] = heap[smallest], heap[i]
        i = smallest
```

### Building a Heap in O(n)

Inserting n elements one by one costs O(n log n). **Heapify** does better: call sift-down on every non-leaf node, starting from the last one and moving backwards to the root. Most nodes are near the bottom and sift down only a little, so the total work is O(n).

### Heap Operations Summary

| Operation | Time |
|---|---|
| Peek at min (or max) | O(1) |
| Insert | O(log n) |
| Remove min (or max) | O(log n) |
| Build from n elements | O(n) |
| Search for an arbitrary value | O(n) |

### Heaps in Python

Python's `heapq` module provides a min-heap on a plain list:

```python
import heapq

tasks = []
heapq.heappush(tasks, (2, "write report"))
heapq.heappush(tasks, (1, "fix bug"))
heapq.heappush(tasks, (3, "reply to email"))
print(heapq.heappop(tasks))        # (1, 'fix bug')
```

For a max-heap, push negated priorities.

## Applications of Heaps

- **Priority queues:** CPU scheduling, hospital triage, event simulations.
- **Heap sort:** build a max-heap, then repeatedly move the maximum to the end (Chapter 6).
- **Top-k problems:** to find the k largest of n items, keep a *min-heap of size k*; for each new item, if it beats the smallest in the heap, replace it. Time O(n log k), which is far better than sorting everything when k is small.
- **Merging k sorted lists:** keep the current head of each list in a min-heap and repeatedly take the smallest.
- **Running median:** keep a max-heap for the lower half of the numbers and a min-heap for the upper half.
- **Graph algorithms:** Dijkstra's shortest paths and Prim's minimum spanning tree (Chapter 9).

## Hash Tables

Suppose we want to store student records and look them up by roll number instantly. A **hash table** does this by computing an array index directly from the key.

### Hash Functions

A **hash function** maps a key to an integer, which is reduced to an index in an array of **buckets**:

```
index = hash(key) % number_of_buckets
```

A good hash function:

- is **deterministic**: the same key always gives the same hash;
- is **fast** to compute;
- spreads keys **uniformly** across buckets, so similar keys land in different places.

For strings, a common approach is a polynomial rolling hash: treat characters as digits in some base and combine them, taking the remainder by a large number.

### Collisions

Two different keys can hash to the same bucket. This is a **collision**, and it is unavoidable: there are far more possible keys than buckets. There are two main ways to handle collisions.

#### Separate Chaining

Each bucket holds a small list of all entries that hash there. To look up a key, hash it, then scan that bucket's list.

```python
class HashMap:
    def __init__(self, size=8):
        self.buckets = [[] for _ in range(size)]

    def put(self, key, value):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))

    def get(self, key):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for k, v in bucket:
            if k == key:
                return v
        raise KeyError(key)
```

#### Open Addressing

All entries live directly in the array. On a collision, **probe** for another empty slot:

- **Linear probing:** try the next slot, then the next (index + 1, + 2, ...). Simple and cache-friendly, but it causes **clustering**, long runs of filled slots.
- **Quadratic probing:** try index + 1, + 4, + 9, ... which reduces clustering.
- **Double hashing:** use a second hash function to decide the step size.

Deleting in open addressing needs care: mark slots as "deleted" (tombstones) rather than empty, or later searches may stop too early.

### Load Factor and Resizing

The **load factor** is the number of entries divided by the number of buckets. As it grows, collisions become more frequent and operations slow down. When the load factor passes a threshold (often around 0.7), the table **resizes**: it allocates a bigger array, typically double the size, and **rehashes** every entry into it. Like dynamic arrays, the occasional O(n) resize averages out to amortised O(1).

### Performance

| Operation | Average | Worst case |
|---|---|---|
| Insert | O(1) | O(n) |
| Lookup | O(1) | O(n) |
| Delete | O(1) | O(n) |

The worst case happens when many keys collide, for example with a poor hash function or deliberately chosen keys. Good hash functions and resizing keep the average case the one you actually see.

> **Key idea:** Hash tables give up ordering to gain speed. They cannot efficiently answer "what is the smallest key?" or "list keys between 10 and 20". Use a balanced BST when you need order.

### Sets and Maps

Python's `dict` and `set`, Java's `HashMap` and `HashSet`, and C++'s `unordered_map` are all hash tables. Keys must be **hashable**: they must not change while stored, which is why Python lists cannot be dictionary keys but tuples can.

## Classic Hashing Problems

**Two sum:** find two numbers adding to a target in O(n).

```python
def two_sum(nums, target):
    seen = {}                          # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i
```

**Frequency counting:** count words in a document with a dictionary, in O(n).

**Grouping anagrams:** use the sorted letters of each word as a key: "eat", "tea" and "ate" all map to "aet".

**Detecting duplicates** and **caching** (memoization, Chapter 5) also rely on hash tables.

### Beyond Basic Hash Tables

- **Cryptographic hashes** such as SHA-256 are designed so that collisions are practically impossible to find. They are used for passwords, digital signatures and file integrity checks, not for ordinary hash tables, because they are slower.
- **Bloom filters** use several hash functions and a bit array to test set membership with very little memory, allowing occasional false positives but never false negatives.
- **Consistent hashing** spreads data across many servers so that adding or removing a server moves only a small fraction of the keys.

## Heap vs Hash Table vs Balanced BST

| Need | Best structure |
|---|---|
| Repeatedly get the min or max | Heap |
| Look up by exact key | Hash table |
| Keep keys ordered, range queries | Balanced BST |

## Summary

- A binary heap is a complete tree with the heap property, stored compactly in an array.
- Insert and remove-min are O(log n) via sift-up and sift-down; peek is O(1); heapify builds a heap in O(n).
- Heaps implement priority queues and solve top-k, merging and running-median problems.
- Hash tables map keys to buckets with a hash function, giving average O(1) operations.
- Collisions are handled by chaining or open addressing; resizing keeps the load factor low.
- Hash tables are unordered; choose a heap or a BST when order matters.

## Practice Questions

1. Insert 7, 2, 9, 1, 5 into an empty min-heap and show the array after each insertion.
2. For the node at index 4 in an array heap, what are the indexes of its parent and children?
3. How would you find the 10 largest numbers in a stream of one million numbers efficiently?
4. Compare separate chaining and linear probing.
5. What is the load factor, and why do hash tables resize?
