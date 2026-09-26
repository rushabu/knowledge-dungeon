# Greedy Algorithms and Dynamic Programming

Many problems ask for the *best* answer: the cheapest route, the most valuable set of items, the fewest coins. Trying every possibility is usually far too slow. This chapter covers two powerful strategies for optimisation problems. **Greedy algorithms** make the best-looking choice at each step and never look back. **Dynamic programming** breaks a problem into overlapping subproblems and remembers their answers.

## Greedy Algorithms

A **greedy algorithm** builds a solution piece by piece, always choosing the option that looks best *right now*.

Greedy algorithms are simple and fast, but they only give the optimal answer for problems with two properties:

- **Greedy choice property:** a locally optimal choice can always be extended to a globally optimal solution.
- **Optimal substructure:** an optimal solution contains optimal solutions to its subproblems.

> **Key idea:** A greedy algorithm must be *proved* correct for each problem. If you cannot argue why the greedy choice is safe, test it against a counterexample before trusting it.

### Activity Selection

You have activities with start and finish times and one room. Schedule as many non-overlapping activities as possible.

Greedy rule: **always pick the activity that finishes earliest** among those that start after the last chosen activity ends.

```python
def select_activities(activities):          # list of (start, finish)
    chosen, last_end = [], float("-inf")
    for start, finish in sorted(activities, key=lambda a: a[1]):
        if start >= last_end:
            chosen.append((start, finish))
            last_end = finish
    return chosen
```

Why it works: finishing early leaves the most room for everything else. Sorting dominates, so the time is O(n log n).

### Fractional Knapsack

A thief can carry W kilograms and may take *fractions* of items (such as gold dust). Greedy rule: take items in order of **value per kilogram**, highest first, taking a fraction of the last one if needed. This is optimal.

### Coin Change: When Greedy Fails

To pay an amount with the fewest coins, the greedy rule "always use the largest coin that fits" works for Indian currency (1, 2, 5, 10, 20, ...). But with coins {1, 3, 4} and amount 6, greedy takes 4 + 1 + 1 (three coins), while 3 + 3 (two coins) is better. Greedy is not always correct, and this problem needs dynamic programming in general.

### Other Greedy Algorithms

- **Huffman coding:** builds optimal prefix codes for data compression by repeatedly merging the two least frequent symbols.
- **Dijkstra's algorithm, Prim's algorithm and Kruskal's algorithm** (Chapter 9) are all greedy.
- **Job sequencing with deadlines** and **minimum platforms at a railway station** are classic greedy exercises.

## Dynamic Programming

**Dynamic programming (DP)** solves problems whose subproblems **overlap**: the same smaller problem appears again and again. Instead of solving it repeatedly, DP solves each subproblem once and stores the answer.

DP applies when a problem has:

1. **Optimal substructure:** the best solution is built from best solutions to subproblems.
2. **Overlapping subproblems:** the same subproblems recur.

Divide and conquer (like merge sort) also splits problems, but its subproblems are independent, so there is nothing to reuse.

### Two Styles

Recall the naive Fibonacci from Chapter 5, which takes O(2^{n}) time.

**Top-down (memoization):** keep the recursive structure, but cache results.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

**Bottom-up (tabulation):** fill a table from the smallest subproblems upwards.

```python
def fib(n):
    if n < 2:
        return n
    prev, cur = 0, 1
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur
```

Both run in O(n). The bottom-up version also avoids recursion and, here, needs only O(1) space.

### How to Design a DP Solution

1. **Define the state:** what does dp[i] (or dp[i][j]) mean, in words?
2. **Write the recurrence:** how does a state depend on smaller states?
3. **Set the base cases.**
4. **Choose the order** of computation so that dependencies are computed first.
5. **Find the answer** in the table.
6. **Optimise space** if only the previous row or two are needed.

## Classic DP Problems

### Climbing Stairs

You can climb 1 or 2 steps at a time. How many ways are there to reach step n?

- State: ways[i] = number of ways to reach step i.
- Recurrence: ways[i] = ways[i - 1] + ways[i - 2] (the last move was either 1 step or 2 steps).
- Base: ways[0] = 1, ways[1] = 1.

It is Fibonacci in disguise.

### Coin Change (Minimum Coins)

```python
def min_coins(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount               # dp[a] = fewest coins to make a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

min_coins([1, 3, 4], 6)    # 2  (3 + 3), where greedy gave 3
```

Time O(amount x number of coins).

### 0/1 Knapsack

Each item has a weight and value; you either take it whole or leave it. Maximise value within capacity W.

- State: dp[i][w] = best value using the first i items with capacity w.
- Recurrence: dp[i][w] = max(dp[i-1][w], value_i + dp[i-1][w - weight_i]) if item i fits; otherwise dp[i-1][w].

```python
def knapsack(weights, values, W):
    dp = [0] * (W + 1)
    for wt, val in zip(weights, values):
        for w in range(W, wt - 1, -1):      # go backwards so each item is used once
            dp[w] = max(dp[w], val + dp[w - wt])
    return dp[W]
```

Time O(n x W), space O(W).

| | Fractional knapsack | 0/1 knapsack |
|---|---|---|
| Can split items? | Yes | No |
| Correct method | Greedy by value/weight | Dynamic programming |
| Time | O(n log n) | O(n x W) |

### Longest Common Subsequence (LCS)

A **subsequence** keeps characters in order but may skip some. The LCS of "ABCBDAB" and "BDCABA" has length 4 (for example "BCBA").

- State: dp[i][j] = LCS length of the first i characters of X and the first j of Y.
- Recurrence: if X[i-1] == Y[j-1], dp[i][j] = dp[i-1][j-1] + 1; otherwise dp[i][j] = max(dp[i-1][j], dp[i][j-1]).

```python
def lcs(x, y):
    dp = [[0] * (len(y) + 1) for _ in range(len(x) + 1)]
    for i in range(1, len(x) + 1):
        for j in range(1, len(y) + 1):
            if x[i - 1] == y[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]
```

Time O(m x n). LCS underlies `diff` tools and DNA sequence comparison.

### Edit Distance

The **edit distance** between two words is the minimum number of insertions, deletions and substitutions needed to turn one into the other ("kitten" to "sitting" needs 3). Its DP table looks just like LCS. Spell checkers use it to suggest corrections.

### Longest Increasing Subsequence (LIS)

Find the longest subsequence in which values strictly increase. A simple DP is O(n^{2}): dp[i] is the length of the longest increasing subsequence ending at i. A clever method with binary search achieves O(n log n).

> **Key idea:** Most DP problems follow a few patterns: 1-D sequences (stairs, LIS), two strings (LCS, edit distance), choose-or-skip items (knapsack) and grids (unique paths). Recognising the pattern is half the solution.

## Greedy vs Dynamic Programming

| | Greedy | Dynamic programming |
|---|---|---|
| Decisions | One choice per step, never revisited | Considers all choices via subproblems |
| Speed | Usually faster | Usually slower, uses more memory |
| Correctness | Only for problems with the greedy choice property | Whenever there is optimal substructure |
| Examples | Activity selection, Huffman, Dijkstra | Knapsack, LCS, edit distance, coin change |

A good strategy: try to find a greedy rule and a counterexample to it. If you find a counterexample, switch to DP.

## Summary

- Greedy algorithms take the best local choice at each step; they are fast but must be proved correct.
- Activity selection, fractional knapsack, Huffman coding, Dijkstra, Prim and Kruskal are greedy.
- Dynamic programming reuses answers to overlapping subproblems, top-down with memoization or bottom-up with tables.
- Design DP by defining the state, the recurrence, the base cases and the computation order.
- Classic DP problems include climbing stairs, coin change, 0/1 knapsack, LCS, edit distance and LIS.
- When a greedy rule has a counterexample, dynamic programming is often the answer.

## Practice Questions

1. Apply activity selection to (1,4), (3,5), (0,6), (5,7), (3,9), (5,9), (6,10), (8,11).
2. Show that greedy coin change fails for coins {1, 5, 6, 9} and amount 11.
3. Fill the DP table for the 0/1 knapsack with weights [1, 3, 4], values [15, 20, 30] and capacity 4.
4. Compute the LCS length of "AGGTAB" and "GXTXAYB".
5. Explain the difference between memoization and tabulation.
