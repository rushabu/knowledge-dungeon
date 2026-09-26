# Trees and Binary Search Trees

Arrays, linked lists, stacks and queues are all **linear**: each element has one successor. Many kinds of data are **hierarchical** instead: a company's reporting structure, the folders on your computer, the structure of an HTML page, or a family tree. **Trees** represent hierarchy naturally, and **binary search trees** add ordering to allow fast searching, insertion and deletion.

## Tree Vocabulary

A **tree** is a collection of **nodes** connected by **edges**, with no cycles, and with one special node called the **root**.

- **Parent / child:** a node directly above / below another.
- **Siblings:** nodes with the same parent.
- **Leaf:** a node with no children.
- **Internal node:** a node with at least one child.
- **Subtree:** a node together with all its descendants.
- **Depth** of a node: the number of edges from the root to it. The root has depth 0.
- **Height** of a tree: the number of edges on the longest path from the root to a leaf.
- **Degree** of a node: its number of children.

A tree with n nodes always has exactly n - 1 edges.

## Binary Trees

In a **binary tree**, each node has at most two children, called **left** and **right**.

```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
```

Special kinds of binary trees:

- **Full:** every node has 0 or 2 children.
- **Complete:** every level is filled except possibly the last, which is filled from left to right. Heaps use complete trees (Chapter 8).
- **Perfect:** all internal nodes have two children and all leaves are at the same depth. A perfect tree of height h has 2^{h+1} - 1 nodes.
- **Balanced:** the heights of the left and right subtrees of every node differ by a small amount, keeping the height about log n.
- **Degenerate (skewed):** every node has one child, so the tree is really a linked list.

> **Key idea:** The height of a tree controls the speed of most tree operations. A balanced tree with a million nodes is only about 20 levels deep; a skewed one is a million levels deep.

## Tree Traversals

To **traverse** a tree is to visit every node once. There are two families.

### Depth-First Traversals

These go deep along a branch before backtracking. They differ only in *when* the node itself is visited.

- **Preorder** (node, left, right): useful for copying a tree or printing folder structures.
- **Inorder** (left, node, right): on a binary search tree, visits values in **sorted order**.
- **Postorder** (left, right, node): useful for deleting a tree or computing folder sizes, where children must be finished first.

```python
def inorder(node, out):
    if node:
        inorder(node.left, out)
        out.append(node.val)
        inorder(node.right, out)
```

For this tree:

```
        8
       / \
      3   10
     / \    \
    1   6    14
```

- Preorder: 8, 3, 1, 6, 10, 14
- Inorder: 1, 3, 6, 8, 10, 14
- Postorder: 1, 6, 3, 14, 10, 8

### Breadth-First (Level-Order) Traversal

Visit nodes level by level, left to right, using a queue.

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        node = q.popleft()
        out.append(node.val)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
    return out
```

Level order for the tree above: 8, 3, 10, 1, 6, 14.

All traversals take O(n) time. Recursive depth-first traversals use O(h) stack space, where h is the height.

## Recursive Thinking with Trees

Trees are recursive by nature: a tree is a root plus two smaller trees. Many problems become short recursive functions.

```python
def height(node):
    if node is None:
        return -1                      # an empty tree has height -1
    return 1 + max(height(node.left), height(node.right))

def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)
```

## Binary Search Trees (BST)

A **binary search tree** is a binary tree with an ordering rule:

- every value in a node's **left** subtree is **smaller** than the node, and
- every value in its **right** subtree is **larger**.

The example tree above is a BST.

### Searching

Start at the root. If the target is smaller, go left; if larger, go right; stop when you find it or reach an empty spot.

```python
def search(node, target):
    while node and node.val != target:
        node = node.left if target < node.val else node.right
    return node
```

This is binary search on a tree: O(h), where h is the height.

### Insertion

Search for the value; when you fall off the tree, attach a new node there.

```python
def insert(node, val):
    if node is None:
        return TreeNode(val)
    if val < node.val:
        node.left = insert(node.left, val)
    elif val > node.val:
        node.right = insert(node.right, val)
    return node
```

### Deletion

Deletion has three cases:

1. **Leaf:** simply remove it.
2. **One child:** replace the node with its child.
3. **Two children:** replace the node's value with its **inorder successor** (the smallest value in its right subtree), then delete that successor, which has at most one child.

### Other Useful Operations

- **Minimum:** keep going left. **Maximum:** keep going right.
- **Sorted output:** inorder traversal.
- **Range queries:** visit only subtrees that can contain values in the range.

### Validating a BST

A common mistake is to check only that each node's children are on the correct side. The rule applies to *entire subtrees*, so pass down allowed bounds:

```python
def is_bst(node, lo=float("-inf"), hi=float("inf")):
    if node is None:
        return True
    if not (lo < node.val < hi):
        return False
    return is_bst(node.left, lo, node.val) and is_bst(node.right, node.val, hi)
```

## The Balance Problem

BST operations cost O(h). If values are inserted in random order, the height is about log n on average. But inserting already sorted values (1, 2, 3, 4, ...) builds a skewed tree where every node only has a right child, so h = n and operations become O(n).

**Self-balancing BSTs** fix this by restructuring the tree after insertions and deletions.

### AVL Trees

An **AVL tree** keeps, at every node, a **balance factor** (height of left subtree minus height of right subtree) of -1, 0 or +1. When an insertion or deletion breaks this, the tree performs **rotations**:

- **Left-Left case:** single right rotation.
- **Right-Right case:** single left rotation.
- **Left-Right case:** left rotation on the child, then right rotation on the node.
- **Right-Left case:** right rotation on the child, then left rotation on the node.

A rotation is a local rearrangement of three nodes that preserves the BST ordering while reducing the height.

### Red-Black Trees

A **red-black tree** colours nodes red or black and enforces rules (for example, no two reds in a row, and every path from a node to its leaves has the same number of blacks). It is a little less strictly balanced than AVL but needs fewer rotations on updates. Java's `TreeMap` and C++'s `std::map` use red-black trees.

| Operation | Unbalanced BST (worst) | Balanced BST (AVL, red-black) |
|---|---|---|
| Search | O(n) | O(log n) |
| Insert | O(n) | O(log n) |
| Delete | O(n) | O(log n) |

## Other Important Trees

- **B-trees and B+ trees:** multi-way trees with many keys per node, designed for disks. Databases and file systems use them for indexes.
- **Tries (prefix trees):** each edge represents a character, so words sharing a prefix share a path. They power autocomplete and spell checkers, and look up a word in O(length of word).
- **Segment trees and Fenwick trees:** answer range queries (sums, minimums) with updates in O(log n).
- **Expression trees:** internal nodes are operators and leaves are operands; postorder traversal evaluates them.

## Summary

- Trees represent hierarchy: a root, parents, children, leaves, depth and height.
- Binary trees have at most two children per node; complete and balanced trees have small height.
- Traversals: preorder, inorder, postorder (depth-first) and level order (breadth-first with a queue).
- In a BST, left subtrees are smaller and right subtrees larger; inorder traversal gives sorted order.
- BST operations cost O(height); sorted insertions create skewed trees.
- AVL and red-black trees rebalance with rotations to guarantee O(log n).
- B-trees, tries and segment trees solve specialised problems.

## Practice Questions

1. Insert 50, 30, 70, 20, 40, 60, 80 into an empty BST and draw the result. Give its inorder and preorder traversals.
2. Delete 30 from your tree in question 1. Which case applies?
3. Why does inserting sorted values into a plain BST make it slow?
4. Write a recursive function that returns the number of leaves in a binary tree.
5. Explain what a trie is and why it is useful for autocomplete.
