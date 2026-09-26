# Advanced SQL: Joins, Grouping and Subqueries

Real questions rarely involve a single table. "Which department has the highest average CGPA?" or "Which students have not submitted any assignment?" need data from several tables, summarised and filtered. This chapter covers the SQL features that make such questions easy: joins, aggregate functions, grouping, subqueries and views.

We will use these tables:

```
student(roll_no, name, dept_id, cgpa)
department(dept_id, dept_name)
course(course_id, title, credits)
enrolls(roll_no, course_id, grade)
```

## Joins in SQL

### Inner Join

An inner join returns only rows that have a match in both tables.

```sql
SELECT s.name, d.dept_name
FROM student s
JOIN department d ON s.dept_id = d.dept_id;
```

`s` and `d` are **table aliases**, which keep queries short and are required when a column name exists in both tables. `JOIN` on its own means `INNER JOIN`.

### Joining Three Tables

```sql
SELECT s.name, c.title, e.grade
FROM student s
JOIN enrolls e ON e.roll_no = s.roll_no
JOIN course  c ON c.course_id = e.course_id
WHERE c.title = 'DBMS';
```

Joins are applied one after another. Each `ON` clause links the new table to the ones already joined.

### Outer Joins

```sql
-- every student, with their courses if they have any
SELECT s.name, e.course_id
FROM student s
LEFT JOIN enrolls e ON e.roll_no = s.roll_no;
```

Students with no enrolments appear once, with `course_id` = NULL. A `RIGHT JOIN` keeps all rows of the right table, and a `FULL OUTER JOIN` keeps unmatched rows from both.

> **Key idea:** To find rows *without* a match, use a LEFT JOIN and then keep the rows where the right side is NULL. This "anti-join" pattern is very common.

```sql
-- students not enrolled in anything
SELECT s.name
FROM student s
LEFT JOIN enrolls e ON e.roll_no = s.roll_no
WHERE e.roll_no IS NULL;
```

### Self Join

A table can be joined with itself. Suppose `employee(emp_id, name, manager_id)`:

```sql
SELECT e.name AS employee, m.name AS manager
FROM employee e
LEFT JOIN employee m ON e.manager_id = m.emp_id;
```

### Cross Join

`CROSS JOIN` produces the Cartesian product: every row paired with every row. It is occasionally useful, for example to create every combination of sizes and colours for a product catalogue.

## Aggregate Functions

Aggregate functions summarise many rows into one value.

| Function | Returns |
|---|---|
| `COUNT(*)` | Number of rows |
| `COUNT(column)` | Number of non-NULL values in the column |
| `SUM(column)` | Total |
| `AVG(column)` | Average (NULLs are ignored) |
| `MIN(column)` / `MAX(column)` | Smallest / largest value |

```sql
SELECT COUNT(*) AS students, AVG(cgpa) AS avg_cgpa, MAX(cgpa) AS topper
FROM student;
```

Note that `COUNT(*)` counts rows, while `COUNT(phone)` counts only rows where phone is not NULL. `COUNT(DISTINCT dept_id)` counts different departments.

## GROUP BY

`GROUP BY` splits rows into groups and computes aggregates for each group.

```sql
SELECT dept_id, COUNT(*) AS students, ROUND(AVG(cgpa), 2) AS avg_cgpa
FROM student
GROUP BY dept_id;
```

Result, one row per department:

```
dept_id | students | avg_cgpa
CSE     | 42       | 8.12
IT      | 38       | 7.86
ECE     | 35       | 7.54
```

> **Key idea:** In a grouped query, every column in the SELECT list must either appear in GROUP BY or be inside an aggregate function. Otherwise SQL cannot know which row's value to show.

## HAVING

`WHERE` filters rows *before* grouping. `HAVING` filters groups *after* grouping.

```sql
SELECT dept_id, AVG(cgpa) AS avg_cgpa
FROM student
WHERE cgpa IS NOT NULL
GROUP BY dept_id
HAVING AVG(cgpa) > 8;
```

This finds departments whose average CGPA is above 8. You cannot write `WHERE AVG(cgpa) > 8`, because averages do not exist until the groups are formed.

The full logical order of a query is now:

1. FROM and JOINs
2. WHERE
3. GROUP BY
4. HAVING
5. SELECT
6. DISTINCT
7. ORDER BY
8. LIMIT

## Subqueries

A **subquery** is a query inside another query.

### Subquery Returning a Single Value

```sql
-- students above the overall average
SELECT name, cgpa
FROM student
WHERE cgpa > (SELECT AVG(cgpa) FROM student);
```

### Subquery with IN

```sql
-- students enrolled in DBMS
SELECT name
FROM student
WHERE roll_no IN (SELECT roll_no FROM enrolls WHERE course_id = 'CS301');
```

### EXISTS and NOT EXISTS

`EXISTS` is true if the subquery returns at least one row.

```sql
-- students who have at least one grade 'A'
SELECT s.name
FROM student s
WHERE EXISTS (
    SELECT 1 FROM enrolls e
    WHERE e.roll_no = s.roll_no AND e.grade = 'A'
);
```

This is a **correlated subquery**: it refers to `s` from the outer query, so it is conceptually re-run for each student. `NOT EXISTS` is the safest way to express "has no matching row".

> **Key idea:** Be careful with `NOT IN` when the subquery can return NULL. If any value is NULL, `NOT IN` returns no rows at all. `NOT EXISTS` does not have this problem.

### ANY and ALL

```sql
SELECT name FROM student
WHERE cgpa > ALL (SELECT cgpa FROM student WHERE dept_id = 'IT');
```

This finds students who beat every IT student. `> ANY` would mean "beats at least one".

## Set Operations

```sql
SELECT roll_no FROM enrolls WHERE course_id = 'CS301'
UNION
SELECT roll_no FROM enrolls WHERE course_id = 'CS302';
```

`UNION` removes duplicates; `UNION ALL` keeps them and is faster. `INTERSECT` and `EXCEPT` (called `MINUS` in Oracle) also exist.

## Views

A **view** is a saved query that behaves like a virtual table.

```sql
CREATE VIEW cse_toppers AS
SELECT roll_no, name, cgpa
FROM student
WHERE dept_id = 'CSE' AND cgpa >= 9;

SELECT * FROM cse_toppers ORDER BY cgpa DESC;
```

Views are useful to:

- **simplify** complicated queries by giving them a name,
- **secure** data by showing users only certain rows or columns, and
- **provide logical data independence**, since programs can keep using the view even if the base tables change.

Most views store no data of their own; the query runs whenever the view is used. A **materialized view** stores the result physically and must be refreshed, which trades freshness for speed.

## Common Table Expressions

A **CTE** (the `WITH` clause) names a temporary result for use in one query. It makes long queries much easier to read.

```sql
WITH dept_avg AS (
    SELECT dept_id, AVG(cgpa) AS avg_cgpa
    FROM student
    GROUP BY dept_id
)
SELECT s.name, s.dept_id, s.cgpa
FROM student s
JOIN dept_avg d ON d.dept_id = s.dept_id
WHERE s.cgpa > d.avg_cgpa;
```

This lists students who are above their own department's average.

## Window Functions in Brief

Window functions compute values across related rows *without* collapsing them into groups.

```sql
SELECT name, dept_id, cgpa,
       RANK() OVER (PARTITION BY dept_id ORDER BY cgpa DESC) AS dept_rank
FROM student;
```

Every student keeps their own row, and gains their rank within their department. `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()` and running totals such as `SUM(x) OVER (ORDER BY date)` are common window functions.

## Summary

- Inner joins keep matches; outer joins also keep unmatched rows; a LEFT JOIN with an IS NULL check finds missing matches.
- Aggregates summarise rows; GROUP BY computes them per group; HAVING filters groups.
- Subqueries can return a value, a list (IN) or a yes/no answer (EXISTS). Prefer NOT EXISTS to NOT IN.
- UNION, INTERSECT and EXCEPT combine query results.
- Views save queries, simplify access and improve security; CTEs make long queries readable.
- Window functions rank and total rows without grouping them away.

## Practice Questions

1. Write a query listing each course title with the number of students enrolled, including courses with zero students.
2. What is the difference between WHERE and HAVING? Give an example that needs both.
3. Find the name of the student(s) with the highest CGPA in each department.
4. Explain why `NOT IN` can return an empty result when the subquery contains NULL.
5. Create a view that shows only name and dept_name for all students, hiding CGPA.
