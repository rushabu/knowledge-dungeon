# Introduction to Databases

Almost every app you use stores data somewhere. Your college portal remembers your marks, a food delivery app remembers your address, and a bank remembers every rupee that moves through your account. This chapter explains what a database is, why we need special software to manage it, and the vocabulary you will use for the rest of this book.

## What Is Data?

**Data** is a collection of raw facts: a name, a roll number, a price, a date. On its own, a single fact rarely means much. The number 82 could be a mark, a temperature or a page count. Data becomes **information** when it is organised and given context: "Riya scored 82 in DBMS" is information.

A **database** is an organised collection of related data, stored so that it can be searched, updated and shared easily. The key word is *organised*. A pile of notebooks full of marks is data; a well-structured table of students, subjects and marks is a database.

> **Key idea:** A database is not just storage. It is storage with structure, so that questions like "which students scored above 80 in DBMS?" can be answered quickly and correctly.

## Life Before Databases: The File System Approach

Before database systems became common, organisations stored data in ordinary files. Each department wrote its own programs and kept its own files. The accounts office had a fees file, the exam cell had a marks file and the library had a borrowers file.

This worked for small systems, but it created serious problems as systems grew.

### Problems with File-Based Systems

1. **Data redundancy.** The same student's name and address were copied into many files. Storage was wasted and the copies easily went out of sync.
2. **Data inconsistency.** When a student changed their phone number, one office updated its file and another did not. Now the organisation had two different "truths".
3. **Difficult access.** Every new question needed a new program. If the principal wanted "all hostel students with pending fees", someone had to write fresh code to combine two files.
4. **Data isolation.** Files were stored in different formats by different programs, so combining them was painful.
5. **Integrity problems.** Rules such as "marks must be between 0 and 100" were buried inside program code. Adding or changing a rule meant changing every program.
6. **Atomicity problems.** If the power failed halfway through transferring money from one account to another, one file might be updated and the other not. Money could vanish.
7. **Concurrent access anomalies.** If two clerks updated the same file at the same time, one person's changes could overwrite the other's.
8. **Security problems.** It was hard to allow the exam cell to see marks while hiding fee details from them.

## The Database Management System

A **Database Management System (DBMS)** is software that stores data in a database and provides tools to define, insert, query, update and protect it. Instead of every program reading raw files, programs ask the DBMS for data, and the DBMS takes care of the details.

Popular examples include MySQL, PostgreSQL, Oracle Database, Microsoft SQL Server and SQLite. SQLite is small enough to live inside a mobile app, while Oracle can run the systems of a large bank.

### What a DBMS Gives You

| Problem with files | How a DBMS helps |
|---|---|
| Redundancy and inconsistency | Data is stored once and shared by all programs |
| Difficult access | A query language (SQL) answers new questions without new programs |
| Integrity rules scattered in code | Constraints are declared once, inside the database |
| Partial updates after failures | Transactions are all-or-nothing |
| Clashing concurrent users | Concurrency control keeps simultaneous work correct |
| Weak security | Users and roles get exactly the permissions they need |

## Levels of Abstraction

A DBMS hides complexity by describing data at three levels. This is called the **three-schema architecture**.

- **Physical level.** How data is actually stored on disk: files, blocks, indexes and compression. Only database administrators and the DBMS itself care about this level.
- **Logical (conceptual) level.** What data is stored and how it is related: the tables, their columns and the rules between them. Developers mostly work here.
- **View (external) level.** What a particular user is allowed to see. A student might see only their own marks; a teacher might see marks for their subject only.

> **Key idea:** Each level hides the details of the level below it. A student viewing their marks does not need to know which disk block holds them.

### Data Independence

Because the levels are separate, we can change one level without breaking the others.

- **Physical data independence** means we can change how data is stored (for example, add an index or move to a faster disk) without changing the logical schema or application programs.
- **Logical data independence** means we can change the logical schema (for example, add a new column) without breaking existing views and programs.

Physical independence is easy to achieve and very common. Logical independence is harder, because programs often depend closely on table structure.

## Schema and Instance

The **schema** is the design of the database: the names of tables, their columns and their types. It changes rarely. The **instance** (or *state*) is the actual data stored at a particular moment. It changes all the time.

Think of a schema as the shape of an empty form and the instance as all the filled-in copies of that form today.

```
Schema:   STUDENT(roll_no, name, branch, year)

Instance: (101, 'Riya',  'CSE', 2)
          (102, 'Arjun', 'IT',  2)
          (103, 'Meera', 'CSE', 3)
```

## Database Languages

A DBMS provides languages for different jobs. In practice they are all part of **SQL** (Structured Query Language), which you will study in detail in Chapter 5.

- **DDL (Data Definition Language)** defines the structure: `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`.
- **DML (Data Manipulation Language)** works with the data itself: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
- **DCL (Data Control Language)** manages permissions: `GRANT`, `REVOKE`.
- **TCL (Transaction Control Language)** manages transactions: `COMMIT`, `ROLLBACK`, `SAVEPOINT`.

```sql
CREATE TABLE student (
    roll_no  INT PRIMARY KEY,
    name     VARCHAR(50) NOT NULL,
    branch   VARCHAR(10),
    year     INT CHECK (year BETWEEN 1 AND 4)
);

INSERT INTO student VALUES (101, 'Riya', 'CSE', 2);

SELECT name FROM student WHERE branch = 'CSE';
```

## Who Uses a Database?

- **End users** use applications built on the database, such as a student checking results online.
- **Application programmers** write the programs that talk to the database.
- **Database designers** decide which tables exist and how they relate.
- **Database administrators (DBAs)** install and tune the DBMS, manage backups, grant permissions and keep the system healthy.

## DBMS Architecture

Most real applications today use a **three-tier architecture**:

1. The **presentation tier** is what the user sees: a website or mobile app.
2. The **application tier** holds business logic, for example the rules for calculating a CGPA.
3. The **data tier** is the DBMS, which stores and protects the data.

The user never talks to the database directly. This keeps the database safer and lets each tier be changed independently. Older systems sometimes used a **two-tier** design, in which a desktop program connected straight to the database.

## Advantages and Disadvantages of a DBMS

Advantages:

- Controlled redundancy and consistent data
- Easy sharing between many users and programs
- Strong security and integrity rules
- Backup and recovery after crashes
- Powerful query languages

Disadvantages:

- The software can be expensive and complex
- It needs skilled people to run it well
- For a tiny, single-user program, a DBMS can be more than you need

## Summary

- Data is raw facts; information is organised data with meaning.
- File-based systems suffer from redundancy, inconsistency, difficult access, integrity, atomicity, concurrency and security problems.
- A DBMS stores data centrally and provides querying, constraints, transactions, concurrency control and security.
- The three-schema architecture separates physical, logical and view levels, giving physical and logical data independence.
- A schema is the design; an instance is the data at one moment.
- SQL includes DDL, DML, DCL and TCL commands.

## Practice Questions

1. List four problems of file-based systems and explain how a DBMS solves each.
2. What is the difference between a schema and an instance? Give an example.
3. Explain physical and logical data independence. Which is harder to achieve, and why?
4. Classify each command as DDL, DML, DCL or TCL: `SELECT`, `GRANT`, `ALTER`, `COMMIT`, `DELETE`.
5. Draw the three-tier architecture for an online exam portal and label each tier.
