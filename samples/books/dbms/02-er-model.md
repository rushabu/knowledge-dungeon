# Data Models and the ER Model

Before we build tables, we need a plan. Just as an architect draws a blueprint before construction starts, a database designer draws a model of the data before writing any SQL. This chapter introduces data models and the most popular design tool of all: the Entity-Relationship (ER) model.

## What Is a Data Model?

A **data model** is a set of concepts used to describe the structure of a database, the relationships between pieces of data and the rules the data must follow. Different data models describe data in different ways.

- **Hierarchical model.** Data is arranged as a tree, with each child having exactly one parent. It was used in early IBM systems. It is fast for fixed queries but awkward when one record belongs to two parents.
- **Network model.** Like the hierarchical model, but a record can have many parents, forming a graph. It is flexible but complicated to program.
- **Relational model.** Data is stored in tables (relations). It is simple, mathematically sound and by far the most widely used today. Chapter 3 covers it in depth.
- **Object-oriented model.** Data is stored as objects with attributes and methods, matching object-oriented programming languages.
- **Document and key-value models.** Used by NoSQL databases such as MongoDB and Redis. Data is stored as flexible JSON-like documents or simple key-value pairs.

> **Key idea:** The ER model is a *conceptual* model. We use it to think and communicate. Afterwards we convert the ER diagram into relational tables.

## The Design Process

Designing a database usually follows these steps:

1. **Requirements analysis.** Talk to users and find out what data must be stored and what questions must be answered.
2. **Conceptual design.** Draw an ER diagram describing entities, attributes and relationships.
3. **Logical design.** Convert the ER diagram into tables (the relational schema).
4. **Schema refinement.** Improve the tables using normalization (Chapter 7).
5. **Physical design.** Choose indexes and storage options for performance.

## Entities and Entity Sets

An **entity** is a real-world thing that can be distinctly identified: a particular student, a particular course, a particular book. An **entity set** is a collection of similar entities, such as all students.

In an ER diagram, an entity set is drawn as a **rectangle**.

### Strong and Weak Entities

A **strong entity** has an attribute (or set of attributes) that uniquely identifies each entity. Every student has a unique roll number, so STUDENT is a strong entity.

A **weak entity** cannot be identified by its own attributes alone. Consider a DEPENDENT of an employee, such as a child. Two different employees might both have a child named "Aarav". The dependent is identified only by combining the employee's ID with the dependent's name. Weak entities are drawn as **double rectangles**, and the attribute that partly identifies them (such as the name) is called a **partial key** or **discriminator**.

## Attributes

An **attribute** is a property of an entity, such as a student's name or date of birth. Attributes are drawn as **ovals** connected to their entity.

| Attribute type | Meaning | Example |
|---|---|---|
| Simple | Cannot be divided further | Roll number |
| Composite | Made of smaller parts | Name (first, middle, last) |
| Single-valued | One value per entity | Date of birth |
| Multivalued | Many values per entity | Phone numbers |
| Stored | Stored directly | Date of birth |
| Derived | Calculated from other attributes | Age (from date of birth) |
| Key | Uniquely identifies an entity | Roll number |

In diagrams, a multivalued attribute has a **double oval**, a derived attribute has a **dashed oval**, and a key attribute is **underlined**.

## Relationships

A **relationship** is an association between entities. "Riya *enrolls in* DBMS" is a relationship between a student and a course. A **relationship set** is a collection of similar relationships. Relationship sets are drawn as **diamonds**.

The **degree** of a relationship is the number of entity sets taking part.

- **Unary (recursive):** one entity set related to itself, such as EMPLOYEE *manages* EMPLOYEE.
- **Binary:** two entity sets, such as STUDENT *enrolls in* COURSE. This is the most common.
- **Ternary:** three entity sets, such as SUPPLIER *supplies* PART to PROJECT.

Relationships can have attributes too. The *grade* a student earns belongs to the enrolment, not to the student alone or the course alone, so it is an attribute of the ENROLLS relationship.

## Cardinality Ratios

**Cardinality** tells us how many entities on one side can be related to entities on the other side.

- **One-to-one (1:1).** Each person has at most one passport, and each passport belongs to one person.
- **One-to-many (1:N).** One department has many employees, but each employee works in one department.
- **Many-to-one (N:1).** The same as one-to-many, read from the other side.
- **Many-to-many (M:N).** A student enrolls in many courses, and a course has many students.

> **Key idea:** Getting cardinality right matters, because it decides how the relationship becomes tables later. An M:N relationship always needs its own table.

## Participation Constraints

**Participation** tells us whether every entity must take part in a relationship.

- **Total participation:** every entity must participate. Every loan must belong to some customer. Drawn with a **double line**.
- **Partial participation:** some entities may not participate. Not every customer has a loan. Drawn with a **single line**.

## A Worked Example: A College Database

Suppose a college wants to store students, courses, departments and instructors.

- STUDENT (roll_no, name, phone numbers, date of birth)
- COURSE (course_id, title, credits)
- DEPARTMENT (dept_id, dept_name)
- INSTRUCTOR (emp_id, name, salary)

Relationships:

- A student **enrolls in** many courses, and each course has many students (M:N). The relationship has a *grade* attribute.
- An instructor **teaches** many courses; each course is taught by one instructor (1:N).
- Each instructor **belongs to** exactly one department; a department has many instructors (N:1, total participation for instructors).

In the diagram, STUDENT and COURSE are rectangles joined by an ENROLLS diamond, with *grade* drawn as an oval on the diamond. Phone numbers appear as a double oval on STUDENT, and roll_no is underlined.

## Extended ER Features

Large designs often need a few more ideas.

### Generalization and Specialization

**Specialization** is top-down: we start from a general entity and split it into more specific ones. PERSON can be specialised into STUDENT and INSTRUCTOR. **Generalization** is bottom-up: we notice that CAR and TRUCK share many attributes and combine them into VEHICLE. Both form an "is-a" hierarchy, in which the lower entities **inherit** the attributes of the higher entity.

Constraints on specialization:

- **Disjoint vs overlapping:** can an entity belong to more than one subclass? A person could be both a student and a teaching assistant (overlapping).
- **Total vs partial:** must every higher-level entity belong to some subclass?

### Aggregation

Sometimes we need a relationship *about* a relationship. Suppose an instructor guides a student on a project, and we want to record which sponsor funds that guidance. **Aggregation** treats the relationship "instructor guides student on project" as a single higher-level entity, which can then take part in another relationship.

## Converting an ER Diagram to Tables

The rules are mechanical, which is part of what makes ER design so useful.

1. **Strong entity:** make a table with all simple attributes. The key attribute becomes the primary key.
2. **Composite attribute:** store only its parts (first_name, last_name).
3. **Multivalued attribute:** make a separate table containing the entity's key and the value, such as STUDENT_PHONE(roll_no, phone).
4. **Weak entity:** make a table containing its partial key plus the primary key of its owner. Together they form the primary key.
5. **1:N relationship:** add the key of the "one" side as a foreign key in the table of the "many" side.
6. **1:1 relationship:** add a foreign key on either side, preferably the side with total participation.
7. **M:N relationship:** make a new table containing the keys of both entities plus any relationship attributes.

```
STUDENT(roll_no, name, dob)
STUDENT_PHONE(roll_no, phone)
COURSE(course_id, title, credits, emp_id)       -- 1:N teaches
INSTRUCTOR(emp_id, name, salary, dept_id)       -- N:1 belongs to
DEPARTMENT(dept_id, dept_name)
ENROLLS(roll_no, course_id, grade)              -- M:N enrolls
```

## Summary

- A data model describes structure, relationships and rules. The relational model dominates today.
- The ER model uses entities (rectangles), attributes (ovals) and relationships (diamonds).
- Attributes can be simple or composite, single or multivalued, stored or derived.
- Cardinality (1:1, 1:N, M:N) and participation (total or partial) describe how entities relate.
- Weak entities depend on an owner entity for identification.
- Specialization, generalization and aggregation handle more complex designs.
- ER diagrams convert to tables through a fixed set of rules.

## Practice Questions

1. Differentiate between a strong and a weak entity with an example of each.
2. Classify these attributes: address, age, email IDs, Aadhaar number.
3. Draw an ER diagram for a library with books, members and loans. Mark cardinality and participation.
4. Why does an M:N relationship need a separate table? Illustrate with STUDENT and COURSE.
5. Explain aggregation with an example of your own.
