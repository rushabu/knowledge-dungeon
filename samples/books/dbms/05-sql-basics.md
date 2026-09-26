# SQL Basics

SQL (pronounced "sequel" or "S-Q-L") is the standard language for relational databases. It was developed at IBM in the 1970s and is now supported by every major DBMS. The good news is that the core of SQL is small and readable. This chapter teaches you to create tables, add and change data, and write simple queries.

## Data Types

Every column has a data type that limits what it can store. Exact names vary slightly between systems, but the common ones are:

| Type | Stores | Example |
|---|---|---|
| `INT` / `INTEGER` | Whole numbers | 42 |
| `DECIMAL(p, s)` | Exact decimals with p digits, s after the point | 8.75 |
| `FLOAT` / `REAL` | Approximate decimals | 3.14159 |
| `CHAR(n)` | Fixed-length text, padded with spaces | 'CSE ' |
| `VARCHAR(n)` | Variable-length text up to n characters | 'Riya' |
| `DATE` | A calendar date | '2026-09-26' |
| `TIMESTAMP` | Date and time | '2026-09-26 10:30:00' |
| `BOOLEAN` | True or false | TRUE |

> **Key idea:** Use `DECIMAL`, not `FLOAT`, for money. Floating-point numbers cannot store values like 0.1 exactly, which causes rounding errors in financial totals.

## Creating Tables (DDL)

```sql
CREATE TABLE course (
    course_id  VARCHAR(8)  PRIMARY KEY,
    title      VARCHAR(60) NOT NULL,
    credits    INT         CHECK (credits BETWEEN 1 AND 6),
    dept_id    VARCHAR(5)  REFERENCES department(dept_id)
);
```

The common column constraints are:

- `PRIMARY KEY`: unique and not NULL.
- `NOT NULL`: a value is required.
- `UNIQUE`: no two rows may share the value.
- `CHECK (condition)`: the value must satisfy a condition.
- `DEFAULT value`: used when no value is given.
- `REFERENCES table(column)`: a foreign key.

### Changing and Removing Tables

```sql
ALTER TABLE course ADD COLUMN semester INT;
ALTER TABLE course DROP COLUMN semester;
ALTER TABLE course RENAME TO subject;

DROP TABLE subject;        -- removes the table and all its data
TRUNCATE TABLE enrolls;    -- removes all rows but keeps the table
```

`DROP` removes the structure itself. `TRUNCATE` empties the table quickly. `DELETE` (below) removes chosen rows and can be rolled back inside a transaction.

## Adding, Changing and Removing Data (DML)

### INSERT

```sql
INSERT INTO student (roll_no, name, branch, cgpa)
VALUES (101, 'Riya', 'CSE', 8.9);

-- several rows at once
INSERT INTO student (roll_no, name, branch, cgpa) VALUES
    (102, 'Arjun', 'IT',  7.4),
    (103, 'Meera', 'CSE', 9.3);
```

Always list the column names. Your insert will then keep working even if someone later adds a new column.

### UPDATE

```sql
UPDATE student
SET cgpa = 9.0
WHERE roll_no = 101;
```

> **Key idea:** An UPDATE or DELETE without a WHERE clause affects **every row** in the table. Always write the WHERE clause first, and run the same condition as a SELECT to check which rows it matches.

### DELETE

```sql
DELETE FROM student WHERE branch = 'ECE';
```

## Querying Data with SELECT

The SELECT statement is the heart of SQL. Its basic shape is:

```sql
SELECT columns
FROM table
WHERE condition
ORDER BY column;
```

### Selecting Columns

```sql
SELECT * FROM student;                 -- every column
SELECT name, cgpa FROM student;        -- chosen columns
SELECT name, cgpa * 9.5 AS percentage FROM student;
```

`AS` gives a column an **alias**, a friendlier name in the result.

### Removing Duplicates

```sql
SELECT DISTINCT branch FROM student;
```

Unlike relational algebra, SQL keeps duplicate rows unless you ask for `DISTINCT`.

### Filtering with WHERE

```sql
SELECT name FROM student WHERE cgpa >= 8.5;
SELECT name FROM student WHERE branch = 'CSE' AND cgpa > 9;
SELECT name FROM student WHERE branch IN ('CSE', 'IT');
SELECT name FROM student WHERE cgpa BETWEEN 7 AND 8.5;   -- inclusive
```

### Pattern Matching with LIKE

`%` matches any sequence of characters; `_` matches exactly one character.

```sql
SELECT name FROM student WHERE name LIKE 'M%';     -- starts with M
SELECT name FROM student WHERE name LIKE '%ya';    -- ends with ya
SELECT name FROM student WHERE name LIKE '_r%';    -- second letter is r
```

### Working with NULL

NULL means "unknown", so `cgpa = NULL` is never true, not even for rows where cgpa is NULL. Use `IS NULL` and `IS NOT NULL` instead.

```sql
SELECT name FROM student WHERE phone IS NULL;
```

Any arithmetic with NULL gives NULL: `5 + NULL` is NULL. The function `COALESCE(phone, 'not given')` replaces NULL with a default value.

### Sorting with ORDER BY

```sql
SELECT name, cgpa FROM student ORDER BY cgpa DESC;
SELECT name, branch, cgpa FROM student ORDER BY branch ASC, cgpa DESC;
```

`ASC` (ascending) is the default. With two sort keys, rows are sorted by branch first, and by cgpa within each branch.

### Limiting Results

```sql
SELECT name, cgpa FROM student ORDER BY cgpa DESC LIMIT 3;   -- top three
```

Some systems use `FETCH FIRST 3 ROWS ONLY` or `TOP 3` instead of `LIMIT`.

## Built-in Functions

| Function | Purpose | Example result |
|---|---|---|
| `UPPER(name)` | Uppercase text | 'RIYA' |
| `LENGTH(name)` | Number of characters | 4 |
| `SUBSTRING(name, 1, 2)` | Part of a string | 'Ri' |
| `ROUND(cgpa, 1)` | Round a number | 8.9 |
| `CURRENT_DATE` | Today's date | 2026-09-26 |
| `COALESCE(a, b)` | First non-NULL value | b if a is NULL |

## How SQL Maps to Relational Algebra

```sql
SELECT DISTINCT name
FROM student
WHERE branch = 'CSE';
```

This is exactly `pi[name] (sigma[branch = 'CSE'] (STUDENT))`. The FROM clause names the relation, WHERE is selection and the SELECT list is projection. `DISTINCT` is needed to get the set behaviour of algebra.

## The Logical Order of a Query

We write SELECT first, but the DBMS logically processes the clauses in this order:

1. `FROM`: find the table(s)
2. `WHERE`: filter rows
3. `SELECT`: choose and compute columns
4. `DISTINCT`: remove duplicates
5. `ORDER BY`: sort
6. `LIMIT`: cut the result

This explains a common error: you usually cannot use a column alias from SELECT inside WHERE, because WHERE runs first.

## Summary

- Choose data types carefully; use DECIMAL for money.
- DDL (`CREATE`, `ALTER`, `DROP`, `TRUNCATE`) defines structure; DML (`INSERT`, `UPDATE`, `DELETE`, `SELECT`) works with data.
- Always use a WHERE clause with UPDATE and DELETE unless you truly mean every row.
- WHERE supports comparisons, AND/OR, IN, BETWEEN, LIKE and IS NULL.
- ORDER BY sorts, DISTINCT removes duplicates and LIMIT restricts the number of rows.
- Logically, FROM and WHERE are processed before SELECT.

## Practice Questions

1. Write a CREATE TABLE statement for BOOK(isbn, title, author, price, published_on) with sensible types and constraints.
2. What is the difference between DROP, TRUNCATE and DELETE?
3. Why does `WHERE phone = NULL` return no rows? What should you write instead?
4. Write a query to list the names of the five students with the lowest CGPA in the IT branch.
5. Write queries to find students whose names contain the letter "a" as the second-last character.
