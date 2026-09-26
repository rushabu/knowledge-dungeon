# Transactions and the ACID Properties

Imagine you transfer 5,000 rupees to a friend. Your bank must subtract the money from your account and add it to your friend's account. If the system crashes after the first step, the money vanishes. If two transfers from your account run at the same moment, you might overspend. **Transactions** are how a DBMS prevents these disasters.

## What Is a Transaction?

A **transaction** is a sequence of database operations that forms one logical unit of work. It must either happen **completely** or **not at all**.

```sql
BEGIN;
UPDATE account SET balance = balance - 5000 WHERE acc_no = 'A101';
UPDATE account SET balance = balance + 5000 WHERE acc_no = 'B202';
COMMIT;
```

`BEGIN` starts the transaction. `COMMIT` makes all its changes permanent. If anything goes wrong, `ROLLBACK` undoes every change made since `BEGIN`.

### Read and Write Operations

Inside the DBMS, a transaction is described by its reads and writes:

- `read(X)` copies data item X from the database into the transaction's workspace.
- `write(X)` copies the new value of X back to the database.

The transfer above is: read(A), A = A - 5000, write(A), read(B), B = B + 5000, write(B).

## The ACID Properties

Every transaction must satisfy four properties, remembered as **ACID**.

### Atomicity

**All or nothing.** Either every operation of the transaction takes effect, or none does. If the system fails after write(A) but before write(B), the DBMS must undo write(A) when it recovers. Atomicity is handled by the **recovery system**, usually through a log (Chapter 10).

### Consistency

**A transaction takes the database from one valid state to another.** In a transfer, the total money in both accounts must be the same before and after. Consistency depends partly on the programmer writing correct transactions and partly on the DBMS enforcing constraints.

### Isolation

**Concurrent transactions must not interfere with each other.** The result of running transactions at the same time must be the same as running them one after another in *some* order. If another transaction reads the accounts halfway through a transfer, it must not see money that has left A but not yet reached B. Isolation is handled by **concurrency control** (Chapter 9).

### Durability

**Once committed, changes survive failures.** After the bank says "transfer successful", a power cut must not undo it. Durability is achieved by writing changes (or log records describing them) to non-volatile storage before confirming the commit.

> **Key idea:** Atomicity and durability are about *failures*. Isolation is about *other users*. Consistency is about *correctness* of the data.

| Property | Question it answers | Mainly ensured by |
|---|---|---|
| Atomicity | Did all of it happen, or none? | Recovery manager (undo) |
| Consistency | Are the rules still true? | Programmer + constraints |
| Isolation | Did others see half-finished work? | Concurrency control |
| Durability | Will it survive a crash? | Recovery manager (redo) |

## Transaction States

A transaction moves through these states:

1. **Active:** it is executing its operations.
2. **Partially committed:** its last operation has run, but changes may still be only in memory.
3. **Committed:** its changes are safely recorded and permanent.
4. **Failed:** an error means it cannot continue normally.
5. **Aborted:** its changes have been rolled back. The system may then restart the transaction or kill it.

A transaction that has committed or aborted is said to be **terminated**.

## Why Run Transactions Concurrently?

It would be simplest to run one transaction at a time, but real systems run many at once because:

- **Throughput improves.** While one transaction waits for disk, another can use the CPU.
- **Waiting time drops.** A short transaction does not have to wait behind a long report.

Concurrency brings risks, however. Without control, these problems appear.

### Lost Update

T1 and T2 both read a seat count of 10. T1 books one seat and writes 9. T2 books one seat and also writes 9. Two seats were sold, but the count only dropped by one. T1's update is **lost**.

### Dirty Read

T1 changes a price and T2 reads the new price. Then T1 fails and rolls back. T2 has used a value that never officially existed. This is a **dirty read** (reading uncommitted data).

### Unrepeatable Read

T1 reads a balance, T2 updates and commits it, and T1 reads the balance again and gets a different value within the same transaction.

### Phantom Read

T1 counts students with CGPA above 9 and gets 12. T2 inserts a new such student and commits. T1 runs the same query again and now gets 13. A **phantom** row appeared.

## Schedules

A **schedule** is the order in which the operations of concurrent transactions are executed.

- A **serial schedule** runs transactions one after another with no interleaving. It is always correct but slow.
- A **concurrent (non-serial) schedule** interleaves operations.

### Serializability

A concurrent schedule is **serializable** if its effect is the same as some serial schedule. Serializability is the formal definition of "correct" isolation.

**Conflict serializability** is the version most often tested. Two operations **conflict** if they belong to different transactions, access the same data item, and at least one of them is a write. The conflicting pairs are read-write, write-read and write-write.

To test a schedule, build a **precedence graph**:

1. Draw a node for each transaction.
2. For each conflicting pair where Ti's operation comes before Tj's, draw an edge Ti -> Tj.
3. If the graph has **no cycle**, the schedule is conflict serializable. A topological order of the graph gives an equivalent serial schedule.

```
Schedule S:  r1(A)  w1(A)  r2(A)  w2(A)  r1(B)  w1(B)

Conflicts: w1(A) before r2(A)  ->  edge T1 -> T2
           w1(A) before w2(A)  ->  edge T1 -> T2
No edge from T2 to T1, so no cycle: S is equivalent to T1 then T2.
```

### Recoverable Schedules

A schedule is **recoverable** if a transaction commits only after every transaction whose data it read has committed. If T2 reads T1's write and commits first, and then T1 aborts, T2 has committed a dirty read that cannot be undone.

A **cascading rollback** happens when one abort forces several other transactions to abort, because they read its uncommitted data. **Cascadeless** schedules avoid this by allowing reads only of committed data.

## Isolation Levels in SQL

Full serializability can be slow, so SQL lets you choose weaker levels:

| Isolation level | Dirty read | Unrepeatable read | Phantom |
|---|---|---|---|
| READ UNCOMMITTED | Possible | Possible | Possible |
| READ COMMITTED | Prevented | Possible | Possible |
| REPEATABLE READ | Prevented | Prevented | Possible |
| SERIALIZABLE | Prevented | Prevented | Prevented |

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

Many databases default to READ COMMITTED. Banking and booking systems often need SERIALIZABLE for critical operations.

## Summary

- A transaction is a unit of work that must happen completely or not at all.
- ACID: atomicity, consistency, isolation, durability.
- States: active, partially committed, committed, failed, aborted.
- Uncontrolled concurrency causes lost updates, dirty reads, unrepeatable reads and phantoms.
- A schedule is correct if it is serializable; use a precedence graph to test conflict serializability.
- Recoverable and cascadeless schedules limit the damage when a transaction aborts.
- SQL isolation levels trade correctness for speed.

## Practice Questions

1. Explain each ACID property using a railway ticket booking example.
2. Describe the lost update problem with a timeline of two transactions.
3. Test whether r1(X) r2(X) w1(X) w2(X) is conflict serializable using a precedence graph.
4. What is a cascading rollback, and how do cascadeless schedules prevent it?
5. Which isolation level would you choose for a report that counts students, and why?
