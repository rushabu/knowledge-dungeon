# Storage, Indexing and Recovery

So far we have treated tables as neat grids of data. Underneath, a database is a collection of files on disk, and disks are slow compared with memory. This final chapter looks at how data is stored, how **indexes** make searches fast, and how a DBMS **recovers** after a crash, delivering the atomicity and durability promised by ACID.

## The Storage Hierarchy

| Level | Speed | Size | Survives power loss? |
|---|---|---|---|
| CPU cache | Fastest | Megabytes | No |
| Main memory (RAM) | Very fast | Gigabytes | No |
| Solid-state drive (SSD) | Fast | Hundreds of GB to TB | Yes |
| Hard disk (HDD) | Slower | Terabytes | Yes |
| Tape / cloud archive | Slowest | Huge | Yes |

Data lives permanently on SSD or HDD, but it can only be processed in memory. Moving data between disk and memory is the main cost of most database operations, so the DBMS tries hard to **minimise disk reads and writes**.

### Blocks and the Buffer Manager

Disks transfer data in fixed-size **blocks** (or **pages**), typically 4 to 16 KB. A DBMS always reads whole blocks, even if it needs one row.

The **buffer manager** keeps recently used blocks in a region of memory called the **buffer pool**. If a requested block is already there (a *buffer hit*), no disk access is needed. When the pool is full, a replacement policy such as **LRU** (least recently used) decides which block to evict. Modified ("dirty") blocks must be written back to disk before eviction.

## File Organisation

How are records arranged inside files?

- **Heap file:** records are placed wherever there is space, in no particular order. Inserts are fast, but finding a record means scanning the whole file.
- **Sequential (sorted) file:** records are kept in order of a search key. Range queries are efficient, but inserts are harder because order must be maintained.
- **Hashed file:** a hash function on a key decides which block a record goes to. Equality searches are very fast.

## Indexes

An **index** is an extra data structure that helps find records quickly, just like the index at the back of a textbook. Without an index, finding the student with roll number 4521 in a million-row table requires a **full table scan**. With an index, the DBMS jumps almost directly to the right block.

```sql
CREATE INDEX idx_student_name ON student(name);
```

> **Key idea:** Indexes speed up reads but slow down writes, because every INSERT, UPDATE and DELETE must also update the index. They also use extra storage. Index the columns you search and join on most often, not every column.

### Types of Indexes

- **Primary (clustering) index:** built on the key by which the file itself is sorted. There can be only one, because a file can only be physically sorted one way.
- **Secondary (non-clustering) index:** built on any other column. The records are not in that order, so the index points to them wherever they are.
- **Dense index:** has an entry for *every* search-key value.
- **Sparse index:** has entries for only *some* values, typically the first key in each block. It works only on sorted files: find the largest entry not bigger than the key you want, then scan that block.
- **Multilevel index:** when an index is itself too large, build an index on the index. This idea leads directly to B+ trees.

## B+ Trees

The **B+ tree** is the most widely used index structure in databases. It is a balanced search tree designed for disks.

Its properties:

- All **leaves are at the same depth**, so every search takes the same number of steps.
- Each node fits in one disk block and holds many keys, often hundreds. This high **fan-out** keeps the tree very shallow: three or four levels can index millions of records.
- **Internal nodes** hold keys and child pointers and are used only for navigation.
- **Leaf nodes** hold keys with pointers to the actual records, and each leaf links to the next leaf.
- Every node except the root is at least half full.

### Searching

Start at the root. At each internal node, follow the pointer for the range containing your key, until you reach a leaf. With a height of 3, a search costs about 3 block reads, plus one to fetch the record.

### Range Queries

Because leaves are linked in sorted order, a query like `cgpa BETWEEN 8 AND 9` finds the first matching leaf, then walks along the leaf chain. This makes B+ trees excellent for ranges and for ORDER BY.

### Insertion and Deletion

To insert, find the correct leaf and add the key. If the leaf overflows, **split** it into two and push the middle key up to the parent. Splits can travel up to the root; if the root splits, the tree grows one level taller. Deletion may cause nodes to **merge** or borrow keys from siblings. These operations keep the tree balanced automatically.

## Hash Indexes

A **hash index** applies a hash function to the key to find a **bucket** directly. Equality lookups (`WHERE roll_no = 4521`) take close to one block access. However, hashing scatters keys randomly, so hash indexes cannot help with range queries or sorting.

**Static hashing** uses a fixed number of buckets and suffers overflow chains as data grows. **Dynamic hashing** schemes such as **extendible hashing** grow the number of buckets as needed.

| Need | Best choice |
|---|---|
| Equality lookups only | Hash index |
| Ranges, sorting, prefix search | B+ tree |
| Small table scanned fully anyway | No index |

## Failures and Recovery

Things go wrong: programs crash, power fails, disks die. The **recovery manager** makes sure that committed transactions survive (durability) and uncommitted ones leave no trace (atomicity).

### Types of Failures

- **Transaction failure:** a logical error (such as dividing by zero) or a system decision (such as a deadlock victim) aborts one transaction.
- **System crash:** power loss or an operating system failure wipes out memory, but disk contents survive.
- **Disk failure:** the disk itself is damaged. Recovery needs backups or replicas.

### The Log

The key tool for recovery is the **log**, a sequential file recording every change. Typical log records are:

```
<T1 start>
<T1, A, 10000, 5000>       -- T1 changed A from 10000 to 5000 (old, new)
<T1, B, 2000, 7000>
<T1 commit>
```

The **write-ahead logging (WAL)** rule says: a log record must be safely written to disk *before* the data change it describes is written to disk. And a transaction is committed only when its commit record is on disk.

### Undo and Redo

After a crash, the recovery manager reads the log.

- Transactions with a `<start>` but **no `<commit>`** are **undone**: their changes are reversed using the old values, restoring atomicity.
- Transactions **with** a `<commit>` are **redone**: their changes are reapplied using the new values, in case they had not reached the disk before the crash. This ensures durability.

Undo and redo are designed to be **idempotent**: doing them twice gives the same result as doing them once, which matters if the system crashes again during recovery.

### Checkpoints

Scanning the whole log after every crash would take too long. Periodically, the DBMS takes a **checkpoint**: it writes all dirty buffers to disk and records `<checkpoint>` in the log, listing the transactions that are active. Recovery then only needs to examine the log from the last checkpoint onwards.

> **Key idea:** WAL plus checkpoints give fast normal operation *and* fast recovery. The **ARIES** algorithm, used by many commercial systems, builds on these ideas with analysis, redo and undo passes.

### Shadow Paging

An alternative to logging is **shadow paging**. The DBMS keeps two page tables: the current one and a shadow copy. Changes are written to new pages. On commit, the current page table becomes the official one in a single atomic step. On abort, the shadow table is simply kept. It is simple, but it fragments data and is rarely used in large systems.

### Protecting Against Disk Failure

- **Backups:** regular full and incremental copies of the database, plus archived logs, allow the database to be rebuilt up to the last committed transaction.
- **RAID:** combines several disks so that data survives one disk failing (for example, mirroring in RAID 1).
- **Replication:** keeps live copies on other servers, which can take over if the main server fails.

## Summary

- Disk access dominates cost; the buffer manager caches blocks in memory.
- Files can be heap, sorted or hashed.
- Indexes speed up searches at the cost of slower writes and extra space.
- B+ trees are balanced, shallow and ideal for both equality and range queries; hash indexes are best for equality only.
- The log, the write-ahead logging rule, undo, redo and checkpoints provide atomicity and durability.
- Backups, RAID and replication protect against disk failure.

## Practice Questions

1. Why does a DBMS read whole blocks rather than individual records?
2. Compare dense and sparse indexes. Why does a sparse index need a sorted file?
3. Explain why a B+ tree of height 3 can index millions of records.
4. When would you prefer a hash index to a B+ tree, and when not?
5. After a crash, the log shows T1 committed and T2 started but did not commit. What does recovery do to each, and why?
