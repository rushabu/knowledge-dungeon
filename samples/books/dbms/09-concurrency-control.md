# Concurrency Control

In the previous chapter we saw what can go wrong when transactions run at the same time, and we defined serializability as the goal. This chapter explains *how* a DBMS actually achieves it. The main techniques are locking, timestamps and multiversioning. We will also study deadlocks, which appear as a side effect of locking.

## Lock-Based Protocols

A **lock** is a marker that a transaction places on a data item to control access by others.

### Types of Locks

- **Shared lock (S):** allows the holder to *read* the item. Many transactions can hold shared locks on the same item at once.
- **Exclusive lock (X):** allows the holder to *read and write* the item. Only one transaction can hold it, and no one else can hold any lock on that item at the same time.

The **compatibility matrix** summarises which requests can be granted:

| Requested \ Held | Shared | Exclusive |
|---|---|---|
| Shared | Yes | No |
| Exclusive | No | No |

If a lock cannot be granted, the requesting transaction **waits** until the other transaction releases its lock.

> **Key idea:** Readers do not block other readers, but a writer blocks everyone and everyone blocks a writer.

### Locking Alone Is Not Enough

Simply locking before each access and unlocking right after does not guarantee serializability. T1 could lock A, update it, unlock it, and only later update B. In between, T2 could read both A and B, and see A after the transfer but B before it. We need rules about *when* locks can be released.

## Two-Phase Locking (2PL)

The **two-phase locking protocol** requires every transaction to work in two phases:

1. **Growing phase:** the transaction may acquire locks but may not release any.
2. **Shrinking phase:** the transaction may release locks but may not acquire any new ones.

The moment a transaction acquires its last lock is called its **lock point**. Transactions following 2PL are serializable in the order of their lock points.

```
T1:  lock-X(A)  read(A)  write(A)  lock-X(B)  unlock(A)  read(B)  write(B)  unlock(B)
     |---------- growing -----------------|------------ shrinking ------------|
```

### Problems with Basic 2PL

- **Deadlocks** can still happen (see below).
- **Cascading rollbacks** can happen: if T1 releases a lock in its shrinking phase, T2 may read T1's uncommitted data, and then T1 aborts.

### Strict and Rigorous 2PL

- **Strict 2PL** holds all *exclusive* locks until the transaction commits or aborts. No one can read uncommitted writes, so cascading rollbacks disappear.
- **Rigorous 2PL** holds *all* locks, shared and exclusive, until commit or abort. Transactions are then serializable in their commit order.

Most commercial databases use strict or rigorous 2PL.

### Lock Conversion

A transaction may **upgrade** a shared lock to exclusive (only in the growing phase) or **downgrade** an exclusive lock to shared (only in the shrinking phase). For example, a transaction might read a row under a shared lock, decide to change it, and then upgrade.

## Deadlocks

A **deadlock** occurs when transactions wait for each other in a cycle, so none can proceed.

```
T1: lock-X(A) ... waits for lock-X(B)
T2: lock-X(B) ... waits for lock-X(A)
```

T1 holds A and wants B; T2 holds B and wants A. Both wait forever.

### Deadlock Prevention

Prevention schemes make deadlock impossible. Two classic schemes use transaction timestamps, where an older transaction has a smaller timestamp.

- **Wait-die (non-preemptive):** if an *older* transaction requests a lock held by a younger one, it waits. If a *younger* transaction requests a lock held by an older one, it **dies** (aborts) and restarts later with its original timestamp.
- **Wound-wait (preemptive):** if an *older* transaction requests a lock held by a younger one, it **wounds** the younger one, forcing it to abort. If a younger one requests a lock held by an older one, it waits.

In both schemes, older transactions are favoured, so every transaction eventually becomes the oldest and finishes. Nobody starves.

Other prevention ideas include acquiring all locks at the start, or always locking items in a fixed order.

### Deadlock Detection and Recovery

Instead of preventing deadlocks, the DBMS can let them happen and fix them.

1. Maintain a **wait-for graph**: draw an edge Ti -> Tj when Ti is waiting for a lock held by Tj.
2. Periodically check the graph for a **cycle**. A cycle means a deadlock.
3. Choose a **victim** transaction, usually the one that has done the least work, and roll it back to break the cycle.

A simpler approach is a **timeout**: if a transaction waits longer than a set time, assume a deadlock and abort it.

> **Key idea:** Prevention wastes some work by aborting transactions that might never have deadlocked. Detection lets transactions run freely, but must pay for checking the graph. Systems with few deadlocks usually prefer detection.

### Starvation

**Starvation** happens when a transaction waits indefinitely, for example because it is repeatedly chosen as a deadlock victim. Fixes include counting how many times a transaction has been rolled back and never choosing it again past a limit.

## Timestamp-Based Protocols

Instead of locks, each transaction receives a unique **timestamp** TS(T) when it starts. The protocol ensures that conflicting operations execute in timestamp order, so the schedule is equivalent to running transactions in the order they started.

For each data item Q, the DBMS stores:

- **W-timestamp(Q):** the largest timestamp of any transaction that wrote Q.
- **R-timestamp(Q):** the largest timestamp of any transaction that read Q.

Rules for a transaction T:

1. **T reads Q:** if TS(T) < W-timestamp(Q), T is trying to read a value that a younger transaction has already overwritten, so T is rolled back. Otherwise the read happens and R-timestamp(Q) is updated.
2. **T writes Q:** if TS(T) < R-timestamp(Q) or TS(T) < W-timestamp(Q), a younger transaction has already used or replaced Q, so T is rolled back. Otherwise the write happens and W-timestamp(Q) is set to TS(T).

Timestamp ordering never causes deadlocks, because nobody waits. However, it can cause many rollbacks and, without extra rules, cascading aborts.

### Thomas' Write Rule

A small improvement: if T tries to write Q but a younger transaction has already written Q (TS(T) < W-timestamp(Q)), the write is **obsolete** and can simply be ignored instead of rolling T back. This allows more schedules to succeed.

## Multiversion Concurrency Control (MVCC)

**MVCC** keeps several versions of each data item. Writers create a new version instead of overwriting, and each reader sees the version that was current when its transaction (or statement) started.

Benefits:

- **Readers never block writers, and writers never block readers.**
- Long reports can run without holding locks that slow everyone else down.

PostgreSQL, MySQL's InnoDB engine and Oracle all use forms of MVCC. Old versions that no transaction needs any more are cleaned up by a background process (called VACUUM in PostgreSQL).

## Optimistic Concurrency Control

**Validation-based** (optimistic) protocols assume conflicts are rare. Each transaction runs in three phases:

1. **Read phase:** read data and make changes in a private workspace.
2. **Validation phase:** check whether any conflicting transaction committed in the meantime.
3. **Write phase:** if validation succeeds, copy the changes into the database; otherwise restart.

This works well when most transactions only read, such as on a news website.

## Lock Granularity

Locks can be placed on items of different sizes: a whole database, a table, a page or a single row. Fine-grained (row) locks allow more concurrency but cost more to manage. Coarse-grained (table) locks are cheap but block more users.

**Multiple-granularity locking** lets a transaction lock at the level it needs. It uses **intention locks** (IS, IX, SIX) on higher levels to announce "I hold or will hold locks further down". For example, before locking a row in exclusive mode, a transaction places an IX lock on the table.

## Summary

- Shared locks allow reading by many; exclusive locks allow writing by one.
- Two-phase locking (grow then shrink) guarantees serializability; strict 2PL also prevents cascading rollbacks.
- Deadlocks can be prevented (wait-die, wound-wait) or detected with a wait-for graph and resolved by choosing a victim.
- Timestamp ordering avoids deadlocks by aborting out-of-order operations; Thomas' write rule ignores obsolete writes.
- MVCC keeps multiple versions so that readers and writers do not block each other.
- Optimistic protocols validate at the end; lock granularity trades concurrency against overhead.

## Practice Questions

1. Draw the lock compatibility matrix and explain it.
2. What are the two phases of 2PL? Why does strict 2PL avoid cascading rollbacks?
3. Compare wait-die and wound-wait with an example involving an old and a young transaction.
4. How does a wait-for graph detect deadlocks?
5. Why can MVCC let long-running reports run without slowing down updates?
