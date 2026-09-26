# The Relational Model and Keys

The relational model, proposed by Edgar F. Codd at IBM in 1970, changed databases forever. Its idea is simple: store all data in tables, and describe queries using mathematics rather than pointers and file positions. Almost every database you will meet in industry is relational. This chapter covers the vocabulary of the model and the keys and constraints that keep data correct.

## Relations, Tuples and Attributes

In the relational model, data is stored in **relations**, which we usually draw as tables.

| Formal term | Everyday term | Meaning |
|---|---|---|
| Relation | Table | A set of rows with the same columns |
| Tuple | Row / record | One entry in the table |
| Attribute | Column / field | One property, such as name |
| Domain | Data type | The allowed values of an attribute |
| Degree | Number of columns | How many attributes a relation has |
| Cardinality | Number of rows | How many tuples a relation has |

For example, the relation STUDENT(roll_no, name, branch, cgpa) has degree 4. If it holds 60 students, its cardinality is 60.

### Properties of a Relation

Because a relation is a mathematical *set* of tuples, it has some important properties:

1. **No duplicate tuples.** Two rows cannot be exactly identical.
2. **Order of tuples does not matter.** Rows have no "first" or "last" in theory.
3. **Order of attributes does not matter**, as long as each value stays with its attribute name.
4. **Values are atomic.** Each cell holds a single, indivisible value. A cell cannot contain a list of phone numbers. This is called **First Normal Form**, which we revisit in Chapter 7.

> **Key idea:** Real SQL databases relax some of these rules. SQL tables *can* contain duplicate rows unless you forbid them with a key. This is why keys are so important.

### NULL Values

Sometimes a value is unknown or does not apply, such as a middle name for someone who has none. The relational model uses a special marker called **NULL**. NULL is not zero and not an empty string; it means "no value here". Comparisons with NULL behave unusually, which you will see in the SQL chapters.

## Relation Schema and Relation Instance

A **relation schema** is written as the relation name followed by its attributes, for example `STUDENT(roll_no, name, branch, cgpa)`. A **relation instance** is the set of tuples in the relation at a given time. A **relational database schema** is the collection of all relation schemas in the database.

## Keys

Keys identify tuples and connect relations together. They are the single most important concept in this chapter.

### Super Key

A **super key** is any set of attributes that uniquely identifies a tuple. In STUDENT, `{roll_no}` is a super key. So is `{roll_no, name}`, because if roll_no alone is unique, adding more attributes keeps it unique. A super key may contain extra, unnecessary attributes.

### Candidate Key

A **candidate key** is a *minimal* super key: a super key from which no attribute can be removed without losing uniqueness. If every student has a unique roll number and also a unique email, then both `{roll_no}` and `{email}` are candidate keys. `{roll_no, name}` is a super key but not a candidate key, because name is unnecessary.

### Primary Key

The **primary key** is the candidate key chosen by the designer to identify tuples. A table has exactly one primary key. Primary key values:

- must be **unique**, and
- must **never be NULL**.

Good primary keys are short, stable and never change. A roll number is a better primary key than a phone number, which might change.

### Alternate Key

The candidate keys that were not chosen as the primary key are called **alternate keys**. If roll_no is the primary key, email is an alternate key. We usually still enforce its uniqueness with a `UNIQUE` constraint.

### Composite Key

A key made of more than one attribute is a **composite key**. In ENROLLS(roll_no, course_id, grade), neither roll_no nor course_id alone is unique, because one student takes many courses and one course has many students. Together, `{roll_no, course_id}` identifies each enrolment.

### Foreign Key

A **foreign key** is an attribute in one relation that refers to the primary key of another relation. It creates a link between tables.

```sql
CREATE TABLE department (
    dept_id   VARCHAR(5) PRIMARY KEY,
    dept_name VARCHAR(40) NOT NULL
);

CREATE TABLE student (
    roll_no  INT PRIMARY KEY,
    name     VARCHAR(50) NOT NULL,
    dept_id  VARCHAR(5) REFERENCES department(dept_id)
);
```

Here `student.dept_id` is a foreign key. It may only contain values that exist in `department.dept_id` (or NULL, if allowed). The table containing the foreign key is the **referencing** (child) table; the other is the **referenced** (parent) table.

### Surrogate Key

Sometimes no natural attribute makes a good key. A **surrogate key** is an artificial value, usually an auto-incrementing number, created only to identify rows. Many real systems use surrogate keys such as `id SERIAL PRIMARY KEY`.

## Integrity Constraints

Constraints are rules that the DBMS enforces automatically, so bad data never enters the database.

### Domain Constraints

Each attribute must take values from its domain. A `cgpa` column of type `DECIMAL(4,2)` with `CHECK (cgpa BETWEEN 0 AND 10)` rejects a value of 11.5 or the text "excellent".

### Key Constraints

Primary key and unique values must not repeat.

### Entity Integrity

**No primary key attribute can be NULL.** If the primary key could be NULL, we could not identify that row.

### Referential Integrity

**A foreign key value must either match an existing primary key value in the referenced table or be NULL.** You cannot enrol a student in department "XYZ" if no such department exists.

Referential integrity raises a question: what should happen when a referenced row is deleted or updated? SQL lets you choose.

| Option | What happens to child rows when the parent is deleted |
|---|---|
| `RESTRICT` / `NO ACTION` | The delete is refused while children exist |
| `CASCADE` | Child rows are deleted too |
| `SET NULL` | The foreign key in child rows is set to NULL |
| `SET DEFAULT` | The foreign key is set to its default value |

```sql
CREATE TABLE enrolls (
    roll_no   INT REFERENCES student(roll_no) ON DELETE CASCADE,
    course_id VARCHAR(8) REFERENCES course(course_id),
    grade     CHAR(2),
    PRIMARY KEY (roll_no, course_id)
);
```

With `ON DELETE CASCADE`, deleting a student automatically deletes their enrolments.

> **Key idea:** Constraints move rules out of application code and into the database, where every program must obey them. This solves the integrity problem of file-based systems from Chapter 1.

## Codd's Rules in Brief

Codd later published twelve rules (numbered 0 to 12) that a truly relational system should follow. You do not need to memorise them all, but a few capture the spirit of the model:

- **Information rule:** all data is represented as values in tables.
- **Guaranteed access rule:** every value can be reached by table name, primary key and column name.
- **Systematic treatment of NULLs:** NULL is handled consistently, independent of data type.
- **Comprehensive data sublanguage:** one language (like SQL) supports definition, manipulation, constraints and transactions.
- **Physical and logical data independence**, as described in Chapter 1.

## Summary

- The relational model stores data as relations (tables) of tuples (rows) and attributes (columns).
- Relations have no duplicate tuples, unordered rows and atomic values.
- A super key uniquely identifies tuples; a candidate key is a minimal super key; the primary key is the chosen candidate key.
- Foreign keys link tables and must satisfy referential integrity.
- Constraints include domain, key, entity integrity and referential integrity.
- Actions such as CASCADE and SET NULL control what happens when referenced rows change.

## Practice Questions

1. Define degree and cardinality. What are the degree and cardinality of a table with 5 columns and 200 rows?
2. In EMPLOYEE(emp_id, email, name, phone), identify the candidate keys, a sensible primary key and the alternate keys.
3. Why must a primary key never be NULL?
4. Explain referential integrity and the effect of `ON DELETE CASCADE` with an example.
5. Is `{roll_no, name}` a candidate key if roll_no alone is unique? Why or why not?
