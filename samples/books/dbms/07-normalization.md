# Functional Dependencies and Normalization

A badly designed table causes trouble even if every query is written perfectly. Data gets repeated, updates go wrong, and some facts cannot be stored at all. **Normalization** is a step-by-step method for splitting tables so that each fact is stored exactly once. It is built on the idea of functional dependencies.

## A Badly Designed Table

Consider this single table that a college might start with:

```
STUDENT_COURSE(roll_no, name, dept, hod, course_id, course_title, grade)

101 | Riya  | CSE | Dr. Rao  | CS301 | DBMS | A
101 | Riya  | CSE | Dr. Rao  | CS302 | OS   | B
103 | Meera | CSE | Dr. Rao  | CS301 | DBMS | A
104 | Kabir | ECE | Dr. Iyer | EC201 | DSP  | B
```

It looks harmless, but it has three kinds of **anomalies**.

- **Update anomaly.** The head of CSE is stored in many rows. If Dr. Rao is replaced, we must change every CSE row. Missing one leaves the data inconsistent.
- **Insertion anomaly.** We cannot record a new course until some student enrols in it, because roll_no is part of the key and cannot be NULL.
- **Deletion anomaly.** If Kabir leaves and we delete his row, we also lose the fact that ECE's head is Dr. Iyer and that the course DSP exists.

> **Key idea:** Anomalies happen when one table stores facts about several different things: students, departments, courses and enrolments. Normalization separates those things.

## Functional Dependencies

A **functional dependency (FD)**, written X -> Y, means: *if two rows agree on X, they must agree on Y*. In other words, X determines Y.

In our table:

- roll_no -> name, dept (a roll number determines the student's name and department)
- dept -> hod (a department has one head)
- course_id -> course_title
- {roll_no, course_id} -> grade (a grade belongs to a student in a course)

X is called the **determinant**. FDs come from the meaning of the data, not from looking at a few rows. Just because every current student has a unique name does not mean name -> roll_no is a real rule.

### Types of Dependencies

- **Trivial FD:** Y is part of X, such as {roll_no, name} -> name. It is always true and tells us nothing.
- **Full functional dependency:** Y depends on the *whole* of X, not just part of it. {roll_no, course_id} -> grade is full.
- **Partial dependency:** Y depends on only part of a composite key. {roll_no, course_id} -> name is partial, because roll_no alone determines name.
- **Transitive dependency:** X -> Y and Y -> Z, so X -> Z indirectly. roll_no -> dept and dept -> hod give roll_no -> hod transitively.

### Armstrong's Axioms

These rules let us derive new FDs from known ones:

1. **Reflexivity:** if Y is a subset of X, then X -> Y.
2. **Augmentation:** if X -> Y, then XZ -> YZ.
3. **Transitivity:** if X -> Y and Y -> Z, then X -> Z.

Useful derived rules include **union** (X -> Y and X -> Z give X -> YZ) and **decomposition** (X -> YZ gives X -> Y and X -> Z).

### Attribute Closure

The **closure** of X, written X+, is the set of all attributes that X determines. To compute it, start with X and keep adding the right side of any FD whose left side is already included.

Example with the FDs above, computing {roll_no}+:

1. Start: {roll_no}
2. roll_no -> name, dept adds: {roll_no, name, dept}
3. dept -> hod adds: {roll_no, name, dept, hod}
4. No more FDs apply.

Since {roll_no}+ does not contain course_id or grade, roll_no alone is not a key. But {roll_no, course_id}+ contains every attribute, so it is a **candidate key**. Closures are the standard way to test whether a set of attributes is a key.

## The Normal Forms

Each normal form removes a particular kind of problem. A table in a higher normal form is automatically in all lower ones.

### First Normal Form (1NF)

A relation is in **1NF** if every attribute holds only **atomic** (single) values, with no repeating groups or lists.

Not in 1NF:

```
roll_no | name | phones
101     | Riya | 98200 11111, 98200 22222
```

Fix: store one phone per row, usually in a separate table STUDENT_PHONE(roll_no, phone).

### Second Normal Form (2NF)

A relation is in **2NF** if it is in 1NF and has **no partial dependencies**: every non-key attribute depends on the *whole* of every candidate key.

Our table has key {roll_no, course_id}, but name and dept depend only on roll_no, and course_title depends only on course_id. We split it:

```
STUDENT(roll_no, name, dept, hod)
COURSE(course_id, course_title)
ENROLLS(roll_no, course_id, grade)
```

2NF only matters when a key is composite. A table with a single-attribute key is automatically in 2NF.

### Third Normal Form (3NF)

A relation is in **3NF** if it is in 2NF and has **no transitive dependencies**: non-key attributes depend only on the key, not on other non-key attributes.

STUDENT still has roll_no -> dept -> hod. We split again:

```
STUDENT(roll_no, name, dept)
DEPARTMENT(dept, hod)
```

A handy way to remember 3NF: every non-key attribute must depend on "the key, the whole key, and nothing but the key".

Formally, a relation is in 3NF if for every non-trivial FD X -> A, either X is a super key or A is part of some candidate key.

### Boyce-Codd Normal Form (BCNF)

**BCNF** is a slightly stricter version of 3NF: for every non-trivial FD X -> Y, **X must be a super key**. There is no exception for key attributes.

Example: TEACHES(student, subject, teacher) where each teacher teaches one subject (teacher -> subject), and each student has one teacher per subject ({student, subject} -> teacher). The table is in 3NF, because subject is part of a candidate key, but not in BCNF, because teacher is not a super key. Splitting into (teacher, subject) and (student, teacher) achieves BCNF.

> **Key idea:** 3NF can always be reached without losing any functional dependency. BCNF removes more redundancy but occasionally makes an FD impossible to check within a single table. In practice, most designers aim for 3NF or BCNF.

### Higher Normal Forms

**4NF** deals with multivalued dependencies: for example, a table storing a teacher's independent sets of subjects and hobbies together. **5NF** deals with join dependencies. They are rarely needed in everyday design.

## Good Decompositions

When we split a table, the split must satisfy two properties.

1. **Lossless join.** Joining the pieces must give back exactly the original table, with no extra, fake rows. A split of R into R1 and R2 is lossless if the common attributes form a key of R1 or of R2. Splitting STUDENT into STUDENT(roll_no, name, dept) and DEPARTMENT(dept, hod) is lossless, because dept is the key of DEPARTMENT.
2. **Dependency preservation.** Every original FD can still be checked within a single piece, without joining.

Lossless join is essential; dependency preservation is highly desirable.

## Denormalization

Normalization reduces redundancy but increases the number of joins. In read-heavy systems, such as reporting dashboards, designers sometimes **denormalize** on purpose, keeping a copy of the department name in the student table for example, to make queries faster. This is a conscious trade-off, not a design mistake, and it must be managed carefully to avoid anomalies.

## Summary

- Poor design causes update, insertion and deletion anomalies.
- A functional dependency X -> Y means X determines Y; closures find keys.
- 1NF: atomic values. 2NF: no partial dependencies. 3NF: no transitive dependencies. BCNF: every determinant is a super key.
- Decompositions must be lossless and should preserve dependencies.
- Denormalization deliberately adds redundancy for read performance.

## Practice Questions

1. Explain the three types of anomalies using an example table of your own.
2. Given R(A, B, C, D) with A -> B and B -> C, compute A+ and find the candidate key if D is determined by A.
3. What is the difference between a partial and a transitive dependency?
4. Normalize ORDER(order_id, customer_id, customer_name, product_id, product_name, qty) to 3NF.
5. Why is 3NF sometimes preferred over BCNF?
