# divars

Symbolic manipulation of Bell operators with dichotomic variables.

This is a Python module that supports some simple algebraic manipulation of
Bell-type operators with ±1-valued measurements. It was developed originally
to automate the symbolic expansion of sum-of-squares decompositions for a
couple of families of Bell operators studied in \[[arXiv:1804.09733
\[quant-ph\]](https://arxiv.org/abs/1804.09733)\] and was included in the
ancillary material accessible from the ArXiv abstract page, but it is a bit
more general than was strictly needed for this work. In particular, it
supports arbitrary numbers of measurements and up to 26 parties.

The module is intended to be used with Python 3 and depends on the SymPy
library for symbolic mathematics. It doesn't work with Python 2. To use it
you'll need to copy the 'divars.py' file into the current working directory
that you are running Python from or into one of the locations that Python is
configured to look for modules in. You can then use it using Python's module
import statements.

Its features are illustrated by some examples below. Its usage should be
fairly self explanatory.

## Examples

You create dichotomic variables by calling the `divars` function with a
string of space-separated names of operators, similar to how the `symbols`
function from SymPy works. The identity is named `Id` and other dichotomic
operators consist of a letter indicating the party followed by an integer
corresponding to the input, e.g., `A1`. After this, you can perform most
arithmetic (addition, subtraction, multiplication, and integer
exponentiation, but not division) of operators with other operators, numbers,
or SymPy objects, using Python's binary operators `+`, `-`, `*`, and `**`.

### Arithmetic

As a first example, the following interactive session shows how to construct and
square the CHSH operator (the `>>>` is the Python prompt):
```Python
>>> from divars import divars
>>> A1, A2, B1, B2 = divars('A1 A2 B1 B2')
>>> S = A1*(B1 + B2) + A2*(B1 - B2)
>>> S
A1 B1 + A1 B2 + A2 B1 - A2 B2
>>> S**2
4 Id - A1 A2 B1 B2 + A1 A2 B2 B1 + A2 A1 B1 B2 - A2 A1 B2 B1
```
Coefficients of dichotomic operators can also be SymPy variables and other
kinds of SymPy objects. For example:
```Python
>>> Id, A1, A2, B1 = divars('Id A1 A2 B1')
>>> from sympy import symbols
>>> x, y = symbols('x y')
>>> (x*Id + y*A1)**2
(x**2 + y**2) Id + 2*x*y A1
>>> (x*A1 + y*A2)**2
(x**2 + y**2) Id + x*y A1 A2 + x*y A2 A1
>>> (x*A1 + y*B1)**2
(x**2 + y**2) Id + 2*x*y A1 B1
```
We can use this to expand sum-of-squares decompositions involving variables
or mathematical expressions analytically as in, for example, the following
simple decomposition for CHSH which involves the square root of two:
```Python
>>> from sympy import sqrt
>>> A1, A2, B1, B2 = divars('A1 A2 B1 B2')
>>> r = 1/sqrt(2)
>>> r*(A1 - r*(B1 + B2))**2 + r*(A2 - r*(B1 - B2))**2
2*sqrt(2) Id - A1 B1 - A1 B2 - A2 B1 + A2 B2
```
This is one way to prove that the quantum expectation value of the CHSH
operator is bounded by 2*sqrt(2).

### Accessing and manipulating the coefficients of polynomials.

The divars module is based around two kinds of objects, each implemented as a
Python class:
- Monomials, which are products of dichotomic operators such as `A1 B1`.
- Polynomials, which are linear combinations of monomials.

The objects returned by the `divars` function mentioned above are of type
`Monomial`. `Polynomial` objects are created and returned as needed by the
arithmetic operators when the result cannot be represented as a monomial, for
example if you add two monomials or if you multiply a monomial by an object
that isn't another monomial.

Polynomials are represented internally as a dictionary with monomials as
keys and coefficients as associated values. The `Polynomial` class is
implemented by inheriting from the built-in Python `dict` class. This means
that basic operations that can be done with dictionaries, such as
lookup/indexing, are also supported for polynomials.

As a simple example, the following code squares CHSH and looks up the
coefficient in front of the term `A1 A2 B1 B2`, and then prints out all of
the monomials and associated coefficients:
```Python
>>> A1, A2, B1, B2 = divars('A1 A2 B1 B2')
>>> S2 = (A1*(B1 + B2) + A2*(B1 - B2))**2
>>> S2[A1*A2*B1*B2]
-1
>>> for m, c in S2.items():
...     print('  S2[{}] = {}.'.format(m, c))
... 
  S2[Id] = 4.
  S2[A1 A2 B1 B2] = -1.
  S2[A1 A2 B2 B1] = 1.
  S2[A2 A1 B1 B2] = 1.
  S2[A2 A1 B2 B1] = -1.
```

The `Polynomial` class also has an `apply` method. It takes a function as an
argument, applies it to each coefficient in the polynomial, and replaces the
coefficient with the result. For example, the following doubles the values of
all the coefficients in `S2` from the previous example:
```Python
>>> S2
4 Id - A1 A2 B1 B2 + A1 A2 B2 B1 + A2 A1 B1 B2 - A2 A1 B2 B1
>>> S2.apply(lambda x: 2*x)
>>> S2
8 Id - 2 A1 A2 B1 B2 + 2 A1 A2 B2 B1 + 2 A2 A1 B1 B2 - 2 A2 A1 B2 B1
```
It is mainly included so that you can apply SymPy functions to manipulate
coefficients, so you can do `P.apply(factor)`, `P.apply(simplify)`, etc.,
after importing these from SymPy.
