# Stacks and Queues

Stacks and queues are restricted lists: you can only add and remove elements at specific ends. That restriction is exactly what makes them useful. A **stack** gives you the most recent item first, and a **queue** gives you the oldest item first. Between them, they power undo buttons, function calls, expression evaluation, printers, schedulers and breadth-first search.

## Stacks: Last In, First Out

A **stack** follows **LIFO** order: the last element added is the first one removed. Think of a stack of plates: you add to the top and take from the top.

Core operations, all **O(1)**:

- `push(x)`: add x to the top.
- `pop()`: remove and return the top element.
- `peek()` / `top()`: look at the top element without removing it.
- `is_empty()`: check whether the stack has no elements.

Popping an empty stack is called **underflow**; pushing onto a full fixed-size stack is **overflow**.

### Implementations

With a dynamic array (a Python list), the end of the list is the top:

```python
stack = []
stack.append(10)       # push
stack.append(20)
top = stack[-1]        # peek -> 20
item = stack.pop()     # pop  -> 20
```

With a linked list, the head is the top, since inserting and deleting at the head is O(1).

```python
class Stack:
    def __init__(self):
        self.head = None
    def push(self, x):
        node = Node(x)
        node.next = self.head
        self.head = node
    def pop(self):
        if self.head is None:
            raise IndexError("pop from empty stack")
        x = self.head.data
        self.head = self.head.next
        return x
```

## Applications of Stacks

### The Call Stack

When a function calls another function, the computer pushes a **stack frame** holding the return address and local variables. When the called function returns, its frame is popped. This is why very deep recursion causes a **stack overflow** error (Chapter 5).

### Undo and Browser Back

Every action is pushed onto a stack. Undo pops the most recent one. A second stack can hold undone actions to support redo.

### Balanced Brackets

Check whether brackets in an expression like `{[()()]}` are balanced.

```python
def balanced(expr):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in expr:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
```

Every closing bracket must match the most recent unmatched opening bracket, which is exactly LIFO. Compilers and code editors use this idea.

### Expression Notation and Evaluation

We normally write **infix** expressions: `3 + 4 * 2`. Computers find **postfix** (Reverse Polish) notation easier, because it needs no brackets or precedence rules: `3 4 2 * +`.

| Infix | Prefix | Postfix |
|---|---|---|
| A + B | + A B | A B + |
| A + B * C | + A * B C | A B C * + |
| (A + B) * C | * + A B C | A B + C * |

**Evaluating postfix** with a stack: scan left to right; push numbers; when you see an operator, pop two numbers, apply the operator, and push the result.

```python
def eval_postfix(tokens):
    stack = []
    for t in tokens:
        if t in "+-*/":
            b, a = stack.pop(), stack.pop()
            stack.append({"+": a + b, "-": a - b, "*": a * b, "/": a / b}[t])
        else:
            stack.append(float(t))
    return stack.pop()

eval_postfix("3 4 2 * +".split())    # 11.0
```

Note the order: the first value popped is the *right* operand.

**Infix to postfix conversion** uses the **shunting-yard algorithm**: output operands immediately, push operators onto a stack, and pop operators of higher or equal precedence before pushing a new one. Opening brackets are pushed; a closing bracket pops operators until the matching opening bracket.

### Monotonic Stacks

A **monotonic stack** keeps its elements in increasing or decreasing order. It solves "next greater element" problems in O(n):

```python
def next_greater(a):
    result = [-1] * len(a)
    stack = []                      # indexes waiting for a greater element
    for i, x in enumerate(a):
        while stack and a[stack[-1]] < x:
            result[stack.pop()] = x
        stack.append(i)
    return result

next_greater([4, 5, 2, 25])         # [5, 25, 25, -1]
```

Each index is pushed and popped at most once, so the total work is O(n), even though there is a loop inside a loop.

## Queues: First In, First Out

A **queue** follows **FIFO** order: the first element added is the first removed, like a line at a ticket counter.

Core operations, all **O(1)** with a good implementation:

- `enqueue(x)`: add x at the **rear**.
- `dequeue()`: remove and return the element at the **front**.
- `front()`: look at the front element.
- `is_empty()`.

### Implementations

A plain Python list is a poor queue, because `list.pop(0)` shifts every element and is O(n). Use `collections.deque`, a double-ended queue with O(1) operations at both ends:

```python
from collections import deque

q = deque()
q.append("A")          # enqueue
q.append("B")
first = q.popleft()    # dequeue -> "A"
```

A linked list with both head and tail pointers also works: enqueue at the tail, dequeue at the head.

### Circular Queues

With a fixed-size array, dequeuing from the front leaves unused space behind. A **circular queue** (ring buffer) wraps the rear index back to the start of the array:

```
rear  = (rear + 1) % capacity
front = (front + 1) % capacity
```

Keeping a count of elements distinguishes a full queue from an empty one. Ring buffers are used for streaming data, keyboard buffers and network packets.

> **Key idea:** The modulo operator lets a fixed array behave like an endless loop, so no space is wasted and nothing needs shifting.

## Variations

- **Deque (double-ended queue):** insert and remove at both ends. It can act as both a stack and a queue. Deques also power the **sliding window maximum** technique.
- **Priority queue:** elements leave in order of **priority**, not arrival. An emergency room treats the most critical patient first. Priority queues are usually implemented with heaps (Chapter 8).

## Applications of Queues

- **Scheduling:** operating systems queue processes for the CPU; printers queue jobs.
- **Breadth-first search:** explores a graph level by level using a queue (Chapter 9).
- **Buffers:** data arriving faster than it can be processed waits in a queue, as with video streaming.
- **Message queues:** in large systems, services communicate by placing messages on queues, such as orders waiting to be processed.

## Stack or Queue?

| Question | Use |
|---|---|
| Need the most recent item first? | Stack |
| Need to process in arrival order? | Queue |
| Need to backtrack (undo, depth-first search)? | Stack |
| Need to explore level by level (shortest path in steps)? | Queue |
| Need the most important item first? | Priority queue |

### Building One from the Other

A classic exercise: implement a queue using two stacks. Push onto an "in" stack. To dequeue, if the "out" stack is empty, pop everything from "in" onto "out" (which reverses the order), then pop from "out". Each element moves at most twice, so operations are amortised O(1).

## Summary

- Stacks are LIFO with O(1) push, pop and peek; queues are FIFO with O(1) enqueue and dequeue.
- Stacks power function calls, undo, bracket matching, expression evaluation and monotonic-stack problems.
- Postfix expressions are evaluated with a stack; the shunting-yard algorithm converts infix to postfix.
- Use `collections.deque` for queues in Python; circular queues reuse a fixed array with modulo arithmetic.
- Deques allow both ends; priority queues serve the highest priority first.
- Queues power scheduling, buffering and breadth-first search.

## Practice Questions

1. Convert `(A + B) * (C - D)` to postfix and prefix.
2. Evaluate the postfix expression `5 1 2 + 4 * + 3 -` step by step.
3. Why is `list.pop(0)` a bad way to dequeue in Python?
4. Implement a queue using two stacks and explain its amortised cost.
5. Use a monotonic stack to find the next greater element for [2, 7, 3, 5, 4, 6, 8].
