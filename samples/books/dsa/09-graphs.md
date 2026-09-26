# Graphs

A **graph** models relationships: people and friendships, cities and roads, web pages and links, courses and prerequisites. Trees and linked lists are special kinds of graphs. Once you can represent a problem as a graph, a large toolbox of algorithms becomes available: searching, shortest paths, spanning trees and ordering tasks.

## Graph Vocabulary

A graph G = (V, E) is a set of **vertices** (nodes) V and **edges** E connecting pairs of vertices.

- **Undirected graph:** edges have no direction, like a two-way road or a Facebook friendship.
- **Directed graph (digraph):** edges have a direction, like a one-way road or an Instagram follow.
- **Weighted graph:** each edge has a number (distance, cost, time).
- **Degree:** the number of edges touching a vertex. In a digraph, **in-degree** counts incoming edges and **out-degree** outgoing ones.
- **Path:** a sequence of vertices connected by edges. A **simple path** repeats no vertex.
- **Cycle:** a path that starts and ends at the same vertex.
- **Connected graph:** every vertex can reach every other (undirected).
- **Connected components:** the separate "islands" of a graph.
- **DAG:** a directed acyclic graph, a directed graph with no cycles. Course prerequisites form a DAG.
- **Dense vs sparse:** dense graphs have close to the maximum V^{2} edges; sparse graphs have far fewer.

## Representing Graphs

### Adjacency Matrix

A V x V table where cell [u][v] is 1 (or the weight) if there is an edge from u to v.

- Checking whether an edge exists: **O(1)**.
- Space: **O(V^{2})**, wasteful for sparse graphs.
- Listing a vertex's neighbours: O(V).

### Adjacency List

Each vertex stores a list of its neighbours.

```python
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}
```

- Space: **O(V + E)**.
- Listing neighbours: O(degree).
- Checking one specific edge: O(degree).

> **Key idea:** Most real-world graphs (roads, social networks, the web) are sparse, so adjacency lists are the usual choice. Use a matrix for small or dense graphs, or when you constantly ask "is there an edge between u and v?".

## Breadth-First Search (BFS)

**BFS** explores the graph in layers: first the start vertex, then all its neighbours, then their neighbours, and so on. It uses a **queue** and marks vertices as visited so each is processed once.

```python
from collections import deque

def bfs(graph, start):
    dist = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in graph[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist                     # number of edges from start to each reachable vertex
```

Time **O(V + E)**. Because BFS reaches vertices in order of distance, it finds **shortest paths in unweighted graphs**, measured in number of edges. Applications include "degrees of separation" in social networks, the fewest moves in a puzzle, and peer discovery in networks.

## Depth-First Search (DFS)

**DFS** goes as deep as possible along one path before backtracking. It uses recursion (or an explicit **stack**).

```python
def dfs(graph, u, visited=None):
    if visited is None:
        visited = set()
    visited.add(u)
    for v in graph[u]:
        if v not in visited:
            dfs(graph, v, visited)
    return visited
```

Time **O(V + E)**. DFS is the basis of many algorithms:

- **Connected components:** run DFS from each unvisited vertex; each run discovers one component.
- **Cycle detection:** in an undirected graph, finding an already visited vertex that is not your parent means a cycle. In a directed graph, reaching a vertex that is still "in progress" on the current path means a cycle.
- **Topological sorting** (below).
- **Maze solving and path finding** with backtracking.

| | BFS | DFS |
|---|---|---|
| Data structure | Queue | Stack / recursion |
| Explores | Level by level | Deep first |
| Shortest path (unweighted) | Yes | No |
| Typical uses | Shortest steps, nearest items | Components, cycles, ordering |

## Topological Sorting

A **topological order** of a DAG lists vertices so that every edge goes from earlier to later: every course appears after its prerequisites.

**Kahn's algorithm** (BFS-based):

1. Compute the in-degree of every vertex.
2. Put all vertices with in-degree 0 into a queue.
3. Repeatedly remove a vertex, add it to the order, and decrease the in-degree of its neighbours; any neighbour reaching 0 joins the queue.
4. If the order contains fewer than V vertices, the graph has a cycle, and no valid order exists.

Topological sort is used in build systems (compile dependencies first), task scheduling and spreadsheet recalculation. It also appears in this very app: rooms in a Knowledge Dungeon unlock in prerequisite order.

## Shortest Paths in Weighted Graphs

### Dijkstra's Algorithm

Dijkstra's algorithm finds the shortest distance from a source to every vertex when all edge weights are **non-negative**.

1. Set the distance to the source as 0 and every other distance to infinity.
2. Repeatedly pick the unvisited vertex with the smallest known distance (using a min-heap).
3. **Relax** its edges: if going through it gives a neighbour a shorter distance, update that distance.

```python
import heapq

def dijkstra(graph, src):             # graph[u] = [(v, weight), ...]
    dist = {src: 0}
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                  # stale entry
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
```

Time **O((V + E) log V)** with a binary heap. Maps and navigation apps use Dijkstra's algorithm and faster variants such as A*, which adds a heuristic estimate of the remaining distance.

> **Key idea:** Dijkstra's algorithm fails with negative edge weights, because it assumes a vertex's distance is final once it is picked.

### Bellman-Ford

**Bellman-Ford** relaxes every edge V - 1 times. It handles **negative weights** and can detect **negative cycles** (if an edge can still be relaxed after V - 1 rounds). It is slower: O(V x E).

### Floyd-Warshall

**Floyd-Warshall** computes shortest paths between **all pairs** of vertices using dynamic programming, in O(V^{3}). It is simple and suits small, dense graphs.

## Minimum Spanning Trees

A **spanning tree** of a connected, undirected graph connects all vertices using exactly V - 1 edges and no cycles. A **minimum spanning tree (MST)** is one with the smallest total edge weight. Example: connect all the villages to the electricity network using the least total cable.

### Kruskal's Algorithm

1. Sort all edges by weight.
2. Take edges from the smallest upwards, adding an edge only if it does not create a cycle.
3. Stop after V - 1 edges.

Cycle checks use the **union-find** (disjoint set) structure, which tracks which vertices are already connected. Time O(E log E).

### Prim's Algorithm

1. Start from any vertex.
2. Repeatedly add the cheapest edge connecting the tree to a vertex not yet in it, using a min-heap.

Time O(E log V). Prim's suits dense graphs; Kruskal's is simple for sparse graphs.

## Union-Find in Brief

Union-find supports two operations:

- **find(x):** which group does x belong to?
- **union(x, y):** merge the groups of x and y.

With **path compression** and **union by rank**, both run in nearly constant amortised time. Beyond Kruskal's algorithm, union-find answers questions like "are these two computers on the same network?".

## Summary

- Graphs model relationships with vertices and edges, which may be directed and weighted.
- Adjacency lists use O(V + E) space and suit sparse graphs; matrices give O(1) edge checks.
- BFS uses a queue and finds shortest paths in unweighted graphs; DFS uses a stack and finds components, cycles and orderings.
- Topological sort orders a DAG so that dependencies come first.
- Dijkstra finds shortest paths with non-negative weights; Bellman-Ford handles negative weights; Floyd-Warshall solves all pairs.
- Kruskal's and Prim's algorithms build minimum spanning trees; union-find supports Kruskal's cycle checks.

## Practice Questions

1. Draw the adjacency matrix and adjacency list for a graph of your choice with 5 vertices and 6 edges.
2. Run BFS from A on the example graph in this chapter and give the distance to each vertex.
3. Give a topological order for: Maths1 -> Maths2, Maths2 -> ML, Programming -> DSA, DSA -> ML.
4. Why does Dijkstra's algorithm fail with negative edge weights? Give a small example.
5. Run Kruskal's algorithm on a weighted graph of your choice and show which edges are chosen.
