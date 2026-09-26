# Operating Systems — Revision Notes

## Processes and Threads
A process is a program in execution. It has its own address space (code, data, heap, stack), a program counter, registers and OS bookkeeping stored in a Process Control Block (PCB).
A process moves between states: New → Ready → Running → Terminated, and Running → Waiting when it requests I/O or waits for an event. A timer interrupt moves a Running process back to Ready. When I/O completes, a Waiting process moves to Ready.
`fork()` creates a child process that is a copy of the parent. Each call doubles the number of processes executing it, so n sequential forks produce 2^n processes. A zombie process has terminated but its parent has not yet called `wait()` to collect its exit status. An orphan process is one whose parent has exited.
A thread is a unit of execution inside a process. Threads of the same process share code, heap and global data and open files, but each thread has its own stack, registers and program counter. Switching between threads of the same process is cheaper than switching processes because the address space (and page tables) do not change.

## CPU Scheduling
The scheduler picks which Ready process runs next. Goals: high CPU utilisation and throughput, low waiting, turnaround and response time.
- First-Come First-Served (FCFS): non-preemptive, simple. Suffers from the convoy effect — short jobs wait behind one long job.
- Shortest Job First (SJF): runs the shortest burst next. It is provably optimal for minimising average waiting time, but needs burst lengths in advance. Its preemptive form is Shortest Remaining Time First.
- Priority scheduling: highest priority first. Low-priority processes can starve; aging (gradually raising the priority of waiting processes) fixes starvation.
- Round Robin (RR): each process gets a fixed time quantum, then goes to the back of the ready queue. A very large quantum makes RR behave like FCFS; a very small quantum causes excessive context-switch overhead.
Waiting time = time spent in the ready queue. Example: bursts P1=6, P2=2, P3=4 all arriving at 0. FCFS waits are 0, 6, 8 (average 4.67). SJF runs P2, P3, P1 with waits 0, 2, 6 (average 2.67).

## Process Synchronization
A race condition occurs when the result depends on the interleaving of concurrent accesses to shared data. Example: two threads each run `counter++` on counter = 5 without a lock; because `counter++` is a read-modify-write, the final value can be 6 or 7.
A critical section is code that accesses shared resources and must not be executed by more than one process at a time. A correct solution must provide mutual exclusion, progress and bounded waiting.
A mutex lock provides mutual exclusion: acquire before the critical section, release after. A spinlock busy-waits; that wastes CPU but is acceptable on multiprocessors when locks are held for a very short time, because it avoids a context switch.
A semaphore is an integer accessed through wait() (P) and signal() (V). A binary semaphore works like a mutex; a counting semaphore initialised to N lets up to N processes use a resource concurrently.

## Deadlocks
A deadlock is a set of processes where each process is waiting for a resource held by another process in the set.
Four necessary (Coffman) conditions: mutual exclusion, hold and wait, no preemption, and circular wait. Breaking any one prevents deadlock — for example, imposing a total order on resource acquisition prevents circular wait.
Handling strategies: prevention (break a condition), avoidance (the Banker's algorithm grants a request only if the system stays in a safe state), detection and recovery, or ignoring the problem.
In a resource-allocation graph, if every resource has a single instance, a cycle means a deadlock definitely exists. With multiple instances per resource, a cycle means deadlock is possible but not certain.
If n processes each need at most m instances of a resource with R instances in total, deadlock is impossible when n(m − 1) + 1 ≤ R: even if every process holds m − 1 instances, one spare instance lets some process finish.

## Memory Management and Paging
Paging splits logical memory into fixed-size pages and physical memory into frames of the same size. The page table maps page numbers to frame numbers. Paging eliminates external fragmentation (though a little internal fragmentation remains in the last page).
A logical address is split into a page number and an offset; with 4 KB (2^12 byte) pages the offset is 12 bits. A 32-bit address with 4 KB pages has 2^20 pages, so a single-level page table with 4-byte entries takes 4 MB.
The Translation Lookaside Buffer (TLB) is a small, fast cache of page-table entries. Effective access time (EAT) = hit ratio × (memory access) + miss ratio × (2 × memory access), ignoring TLB lookup time. With an 80% hit ratio and 100 ns memory access, EAT = 0.8 × 100 + 0.2 × 200 = 120 ns.

## Virtual Memory and Page Replacement
Virtual memory lets a process run without being fully in RAM. Demand paging loads a page only when it is first referenced. A page fault occurs when a referenced page is not in main memory; the OS loads it from disk, replacing a page if no frame is free.
Replacement policies: FIFO (evict the oldest page), LRU (evict the least recently used page), and Optimal (evict the page used farthest in the future — the theoretical best). FIFO can suffer from Belady's anomaly: more frames can cause more page faults. LRU and Optimal do not.
Example with reference string 7, 0, 1, 2, 0, 3, 0, 4 and 3 frames: FIFO causes 7 page faults; LRU causes 6.
Thrashing happens when processes do not have enough frames for their working sets, so the system spends more time paging than executing. Remedies: working-set model, page-fault-frequency control, or running fewer processes.
