# Relational Algebra

SQL is what you type, but relational algebra is what the database thinks. Relational algebra is a small set of operations that take one or two relations as input and produce a new relation as output. Every SQL query is translated into relational algebra inside the DBMS before it is optimised and run. Learning it will make SQL much easier to understand.

## Why Learn Relational Algebra?

- It is **procedural**: an expression describes the steps needed to get a result.
- It is **closed**: every operation returns a relation, so operations can be chained like arithmetic.
- It is the **foundation of query optimisation**. The DBMS rewrites algebra expressions into cheaper equivalent ones.

We will use two example relations throughout this chapter.

```
STUDENT
roll | name  | branch | cgpa
101  | Riya  | CSE    | 8.9
102  | Arjun | IT     | 7.4
103  | Meera | CSE    | 9.3
104  | Kabir | ECE    | 6.8

ENROLLS
roll | course
101  | DBMS
101  | OS
103  | DBMS
104  | DSA
```

## Unary Operations

### Selection (sigma)

**Selection** picks the *rows* that satisfy a condition. It is written as sigma with the condition as a subscript.

```
sigma[branch = 'CSE'] (STUDENT)
```

Result: the rows for Riya and Meera. Conditions can use comparison operators (=, <>, <, >, <=, >=) and can be combined with AND, OR and NOT:

```
sigma[branch = 'CSE' AND cgpa > 9] (STUDENT)      -- only Meera
```

Selection never changes the columns; it only filters rows. The number of rows in the result is at most the number in the input.

### Projection (pi)

**Projection** picks the *columns* you want and discards the rest.

```
pi[name, cgpa] (STUDENT)
```

Because a relation is a set, projection **removes duplicate rows**. Projecting STUDENT on branch gives only three rows: CSE, IT and ECE, even though CSE appears twice in the original.

> **Key idea:** Selection works horizontally (rows). Projection works vertically (columns). In SQL, selection is the WHERE clause and projection is the SELECT list.

### Combining Selection and Projection

Operations can be nested. To find the names of CSE students:

```
pi[name] ( sigma[branch = 'CSE'] (STUDENT) )
```

Read it from the inside out: first keep the CSE rows, then keep only the name column.

### Rename (rho)

**Rename** gives a relation or its attributes a new name. It is needed when a relation is combined with itself, for example to compare two students.

```
rho[S2] (STUDENT)
```

## Set Operations

Set operations combine two relations that are **union-compatible**: they must have the same number of attributes, with matching domains.

- **Union (R ∪ S):** all tuples in R or S or both, with duplicates removed.
- **Intersection (R ∩ S):** tuples in both R and S.
- **Difference (R − S):** tuples in R but not in S.

Example: roll numbers of students enrolled in DBMS *or* OS:

```
pi[roll](sigma[course='DBMS'](ENROLLS)) ∪ pi[roll](sigma[course='OS'](ENROLLS))
```

Result: 101, 103. Roll numbers enrolled in DBMS but *not* OS: only 103.

Union and intersection are commutative (R ∪ S = S ∪ R), but difference is not: R − S is usually different from S − R.

## Cartesian Product

The **Cartesian product** (R × S) pairs every tuple of R with every tuple of S. If R has 4 rows and S has 4 rows, the product has 16 rows, with all the columns of both.

On its own, the product is rarely useful, because most of the pairs are meaningless: it pairs Riya with Kabir's enrolment. Its real value is as a building block for joins.

## Joins

A **join** combines related tuples from two relations. It is equivalent to a Cartesian product followed by a selection, but it is so common that it has its own operator.

### Theta Join

A **theta join** combines tuples that satisfy any condition theta:

```
STUDENT ⋈[STUDENT.roll = ENROLLS.roll] ENROLLS
```

### Equijoin

An **equijoin** is a theta join that only uses equality. The example above is an equijoin. The result contains both roll columns, which are identical.

### Natural Join

A **natural join** automatically joins on all attributes with the same name and keeps only one copy of each. `STUDENT ⋈ ENROLLS` joins on roll:

```
roll | name  | branch | cgpa | course
101  | Riya  | CSE    | 8.9  | DBMS
101  | Riya  | CSE    | 8.9  | OS
103  | Meera | CSE    | 9.3  | DBMS
104  | Kabir | ECE    | 6.8  | DSA
```

Arjun (102) disappears because he has no enrolments. Rows without a match are dropped in an ordinary (inner) join.

### Outer Joins

**Outer joins** keep unmatched rows and fill missing values with NULL.

- **Left outer join:** keeps all rows of the left relation. Arjun would appear with course = NULL.
- **Right outer join:** keeps all rows of the right relation.
- **Full outer join:** keeps unmatched rows from both sides.

> **Key idea:** Use an inner join when you only want matches. Use a left outer join when you want "everyone, plus their matches if any", such as "all students and their courses, including students with no courses".

## Division

**Division** answers "for all" questions. Suppose we want students who are enrolled in *every* course listed in a relation COURSES(course) containing DBMS and OS.

```
ENROLLS ÷ COURSES
```

The result contains roll numbers that appear in ENROLLS paired with *every* course in COURSES. Only 101 (Riya) qualifies. Division is less common than the other operators, but whenever you see "all" or "every" in a query, think of it.

## Writing Queries in Relational Algebra

Let us translate a few English questions.

1. *Names of students with CGPA above 8.*
   `pi[name] (sigma[cgpa > 8] (STUDENT))`
2. *Names of students enrolled in DBMS.*
   `pi[name] (sigma[course = 'DBMS'] (STUDENT ⋈ ENROLLS))`
3. *Roll numbers of students not enrolled in any course.*
   `pi[roll](STUDENT) − pi[roll](ENROLLS)` gives 102.

### Query Trees

A relational algebra expression can be drawn as a **query tree**: leaves are relations and inner nodes are operators. The DBMS optimiser rearranges this tree to make it cheaper. A classic rule is **"push selections down"**: filter rows as early as possible, so later joins process fewer rows. In query 2, selecting DBMS rows from ENROLLS *before* the join is far cheaper than joining everything first.

## Relational Calculus in Brief

Relational algebra says *how* to compute a result. **Relational calculus** says *what* result you want, using logic, without giving steps. It comes in two forms:

- **Tuple relational calculus:** `{ t | t ∈ STUDENT AND t.cgpa > 8 }` means "all tuples t in STUDENT whose cgpa is above 8".
- **Domain relational calculus:** variables range over attribute values instead of whole tuples.

SQL is closer to calculus in spirit, because it is *declarative*: you describe the result and the DBMS decides the steps. Codd proved that relational algebra and safe relational calculus have the same expressive power.

## Summary

- Relational algebra is a procedural, closed set of operations on relations.
- Selection filters rows; projection keeps columns and removes duplicates; rename changes names.
- Union, intersection and difference need union-compatible relations.
- The Cartesian product pairs all tuples; joins combine only related tuples.
- Natural join matches on common attribute names; outer joins keep unmatched rows with NULLs.
- Division answers "for all" queries.
- Optimisers rewrite query trees, for example by pushing selections down.

## Practice Questions

1. What is the difference between selection and projection? Give their SQL equivalents.
2. Why does projection remove duplicates? Show an example.
3. If R has 5 rows and S has 3 rows, how many rows does R × S have?
4. Write relational algebra for: names of CSE students enrolled in OS.
5. When would you use a left outer join instead of a natural join?
