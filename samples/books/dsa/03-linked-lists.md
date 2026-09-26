# Linked Lists

Arrays keep elements side by side, which makes access fast but insertion and deletion slow. A **linked list** takes the opposite approach: each element lives in its own **node**, anywhere in memory, and points to the next node. Inserting or removing a node only means changing a few pointers. This chapter covers singly, doubly and circular linked lists, and the classic techniques for working with them.

## Nodes and Pointers

A node holds two things: the **data** and a **reference** (pointer) to the next node.

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
```

A list is identified by its **head**, the first node. The last node's `next` is `None`, marking the end.

```
head -> [10 | *] -> [20 | *] -> [30 | *] -> None
```

## Singly Linked List Operations

### Traversal

```python
def print_list(head):
    node = head
    while node:
        print(node.data, end=" -> ")
        node = node.next
    print("None")
```

To reach the k-th element we must walk from the head, so access by position is **O(n)**. There is no random access.

### Insert at the Head

```python
def push_front(head, data):
    node = Node(data)
    node.next = head
    return node                # the new head
```

This is **O(1)**: no shifting, unlike an array.

### Insert After a Given Node

```python
def insert_after(prev, data):
    node = Node(data)
    node.next = prev.next
    prev.next = node
```

Also O(1), *if* we already have a reference to `prev`. Finding it may take O(n).

> **Key idea:** Always connect the new node to the rest of the list *before* redirecting the previous node. If you do it in the wrong order, you lose the reference to the rest of the list.

### Insert at the Tail

Without a tail pointer we must walk to the end: O(n). Keeping a separate `tail` reference makes it O(1).

### Delete a Node by Value

```python
def delete(head, value):
    if head and head.data == value:
        return head.next               # deleting the head
    node = head
    while node and node.next:
        if node.next.data == value:
            node.next = node.next.next   # bypass the node
            return head
        node = node.next
    return head
```

The deleted node is skipped over; in Python the garbage collector frees it. In C you must free it yourself.

## Arrays vs Linked Lists

| Operation | Array | Singly linked list |
|---|---|---|
| Access k-th element | O(1) | O(n) |
| Insert / delete at front | O(n) | O(1) |
| Insert / delete at end | O(1) amortised | O(1) with tail pointer (delete needs O(n)) |
| Insert / delete in middle (given position) | O(n) | O(1) after reaching it |
| Extra memory per element | None | One pointer (or two) |
| Cache friendliness | Excellent | Poor (nodes scattered) |

In practice, arrays are faster for most workloads because modern CPUs love contiguous memory. Linked lists win when you frequently insert or delete at known positions, and they are the building blocks of other structures such as stacks, queues, hash-table chains and adjacency lists.

## Doubly Linked Lists

Each node in a **doubly linked list** has pointers to both the next and the previous node.

```
None <- [10] <-> [20] <-> [30] -> None
```

```python
class DNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None
```

Advantages:

- Traverse in both directions.
- Delete a node in O(1) given only a reference to it, because we can reach its predecessor directly.

The cost is an extra pointer per node and more pointers to update on every insertion or deletion. Browser history (back and forward) and LRU caches are classic uses.

### Sentinel (Dummy) Nodes

Special cases for empty lists and for the head and tail make linked-list code error-prone. A **sentinel** is a dummy node that always sits before the first real node (and often after the last). With sentinels, every real node has a predecessor and a successor, so insertion and deletion need no special cases.

## Circular Linked Lists

In a **circular** linked list, the last node points back to the first instead of `None`. It is useful for round-robin scheduling, where a CPU cycles through processes endlessly, and for multiplayer turn order. When traversing, stop when you return to the starting node, or you will loop forever.

## Classic Linked List Techniques

### Reversing a List

```python
def reverse(head):
    prev = None
    node = head
    while node:
        nxt = node.next        # remember the rest
        node.next = prev       # reverse the pointer
        prev = node            # move prev forward
        node = nxt             # move node forward
    return prev                # new head
```

O(n) time, O(1) space. Tracing this on paper with three nodes is the best way to understand pointer manipulation.

### Fast and Slow Pointers

Two pointers moving at different speeds solve several problems elegantly.

**Find the middle node:** the slow pointer moves one step, the fast pointer two. When fast reaches the end, slow is in the middle.

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

**Detect a cycle (Floyd's algorithm):** if the list has a loop, the fast pointer eventually laps the slow one and they meet. If fast reaches `None`, there is no cycle.

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

Both run in O(n) time and O(1) space.

> **Key idea:** "Tortoise and hare" pointers find middles, cycles and the k-th node from the end without extra memory.

### k-th Node from the End

Move one pointer k steps ahead, then move both together. When the leading pointer reaches the end, the trailing pointer is k nodes from the end.

### Merging Two Sorted Lists

```python
def merge(a, b):
    dummy = tail = Node(0)
    while a and b:
        if a.data <= b.data:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next
```

The dummy node avoids special-casing the first element. This merge step is the core of merge sort on linked lists.

## Common Mistakes

- **Losing the head:** moving `head` itself while traversing. Use a separate variable.
- **Null dereference:** accessing `node.next.data` when `node.next` is `None`. Check first.
- **Forgetting to update the head** after inserting or deleting at the front.
- **Infinite loops** in circular lists or after accidentally creating a cycle.

## Summary

- A linked list stores data in nodes connected by pointers, starting from the head.
- Access by position is O(n); insertion and deletion at a known node are O(1).
- Doubly linked lists allow backward traversal and O(1) deletion of a known node.
- Circular lists loop back to the start; sentinel nodes remove special cases.
- Key techniques: iterative reversal, fast and slow pointers (middle, cycle detection, k-th from end) and merging sorted lists.
- Arrays are usually faster in practice, but linked lists underpin stacks, queues, hash chains and graphs.

## Practice Questions

1. Why is access by index O(n) in a linked list but O(1) in an array?
2. Trace the reverse function on the list 1 -> 2 -> 3.
3. Explain why Floyd's cycle detection algorithm always finds a cycle if one exists.
4. Write a function to delete the k-th node from the end in one pass.
5. When would you choose a doubly linked list over a singly linked list?
