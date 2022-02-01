# typedclass

A constrained data structure.

## introduction

This is an playground for exploring the idea of
a `typed` class.

A `typed` class is a `python` class that maintains a
consistent state by carefully managing the mutation
of instance attributes.
Attributes are defined using a model similar to 
`sqlalchemy` or `marshmallow`.  Only defined attributes
can be used (set or accessed). All values are passed
through an arbitrarily strict, user-defined type-checking
function before being saved in the instance.
Arbitrary logic can be run after attribute assignment
to adjust other parts of the structure (to maintain
a consistent state). Required and read-only
attributes are supported.

## wait what?

Python is a dynamic language, lacking strong typing.
There is a movement to add type annotation to the
language, but it is largely focused on
callable argument and return types, and the types
of individual variables and attributes.
So far, this effort is aspirational.

Although a `typed` class does impose typing on each
instance attribute, it goes beyond this to
allow the imposition of
typing on the entire instance.
Controlling the arguments to instance methods or any
other logic that wants to mutate the instance attributes
is not as important as controlling the mutation itself.
