from numbers import Real
from sympy import Add, Mul
from sys import modules

def mult_tuples(x, y):
    ind = 0
    ind0 = min(len(x), len(y))

    while (ind < ind0) and (x[-ind-1] == y[ind]):
        ind += 1

    if ind == 0:
        return x + y
    else:
        return x[:-ind] + y[ind:]

def chomp_empty(seq):
    """Return slice of sequence seq without trailing empty tuples."""
    n = len(seq)

    while (n > 0) and seq[n - 1] == ():
        n -= 1

    return seq[:n]

class Monomial:
    def __init__(self, *args):
        t = tuple(x if type(x) is tuple else (x,) for x in args)
        self.vars = chomp_empty(t)

    def __mul__(self, y):
        if type(y) is Monomial:
            t = tuple(map(mult_tuples, self.vars, y.vars))
            ls, ly = len(self.vars), len(y.vars)
            t += self.vars[ly:] if ls > ly else y.vars[ls:]

            return Monomial(*t)

        elif type(y) is Polynomial:
            return (+self) * y

        else:
            return Polynomial({self: y} if y != 0 else {})

    __rmul__ = __mul__

    def __pos__(self):
        return Polynomial({self: 1})

    def __neg__(self):
        return Polynomial({self: -1})
    
    def __add__(self, y):
        if type(y) is Monomial:
            return Polynomial({self: 1, y: 1} if self != y else {self: 2})
        else:
            return y + self

    def __sub__(self, y):
        if type(y) is Monomial:
            return Polynomial({self: 1, y: -1} if self != y else {})
        else:
            return self + (-y)

    def conjugate(self):
        return Monomial(*(tuple(reversed(ps)) for ps in self.vars))

    def order(self):
        return sum(map(len, self.vars))

    def cmp(self, y):
        ls, ly = self.order(), y.order()

        if ls != ly:
            return -1 if ls < ly else 1

        for u, v in zip(self.vars, y.vars):
            lu, lv = len(u), len(v)

            if (lu != lv):
                return -1 if lu > lv else 1

        for u, v in zip(self.vars, y.vars):
            if u != v:
                return -1 if u < v else 1

        return 0

    def __eq__(self, y):
        return self.cmp(y) == 0
    
    def __neq__(self, y):
        return self.cmp(y) != 0

    def __lt__(self, y):
        return self.cmp(y) < 0

    def __le__(self, y):
        return self.cmp(y) <= 0

    def __gt__(self, y):
        return self.cmp(y) > 0

    def __ge__(self, y):
        return self.cmp(y) >= 0

    def __hash__(self):
        return self.vars.__hash__()

    def __repr__(self):
        if self.order() != 0:
            return ' '.join(filter(None,
                                   (' '.join((chr(ord('A') + n) + str(x)
                                              for x in p))
                                    for n, p in enumerate(self.vars))))
        else:
            return 'Id'

def diop(site, x=1):
    """Make dichotomic variable from site and input number."""
    t = ((),) * site + ((x,),)
    return Monomial(*t)

def divar(name):
    """Make dichotomic variable from (string) name."""
    name = name.upper()

    if name == 'ID':
        return Monomial()
    else:
        return diop(ord(name[0]) - ord('A'), int(name[1:]))

def divars(names):
    """Return a tuple of the dichotomic variables in the string names."""
    return tuple(map(divar, names.split(' ')))

def bind_divars(names, module=modules['__main__']):
    """Create global variable bindings for dichotomic variables.
    
    This creates the dichotomic variables in names (which should be a
    space-separated string) and adds each name and corresponding
    dichotomic variable in the symbol table of module (the top level
    module named '__main__' by default)."""
    bindings = vars(module)

    for name in names.split(' '):
        bindings[name] = divar(name)

class Polynomial(dict):
    def apply(self, f):
        for k in list(self.keys()):
            new_val = f(self[k])

            if new_val != 0:
                self[k] = new_val
            else:
                del self[k]

    def __iadd__(self, y):
        if type(y) is Polynomial:
            for k, v in y.items():
                if k in self:
                    sk = self[k] + v

                    if sk != 0:
                        self[k] = sk
                    else:
                        del self[k]
                else:
                    self[k] = v
        else:
            if y not in self:
                self[y] = 1
            else:
                if self[y] != -1:
                    self[y] += 1
                else:
                    del self[y]  

        return self

    def __add__(self, y):
        p = Polynomial(self.copy())
        p += y
        return p

    def __neg__(self):
        p = Polynomial()
        for k, v in self.items():
            p[k] = -v
        return p

    def __sub__(self, y):
        return self + (-y)

    def __mul__(self, y):
        if type(y) is Polynomial:
            p = Polynomial()

            for ks, vs in self.items():
                for ky, vy in y.items():
                    k, v = ks * ky, vs * vy

                    if k not in p:
                        p[k] = v
                    elif p[k] != -v:
                        p[k] += v
                    else:
                        del p[k]

            return p

        elif type(y) is Monomial:
            return self * (+y)

        elif y != 0:
            p = Polynomial(self.copy())

            for k in self.keys():
                p[k] *= y

            return p
        else:
            return Polynomial({})

    __rmul__ = __mul__

    def __pow__(self, k):
        n = self
        p = n if k % 2 == 1 else Monomial()
        k >>= 1

        while k > 0:
            n = n * n

            if k % 2 == 1:
                p = p * n

            k >>= 1

        return p

    def conjugate(self):
        return Polynomial({m.conjugate(): cf.conjugate()
                               for m, cf in self.items()})

    def __repr__(self):
        keys = sorted(self.keys())

        if len(keys) == 0:
            return '0'

        k, *keys = keys

        x = self[k]

        if x == 1:
            rep = ''
        elif x == -1:
            rep = '-'
        elif type(x) is Add:
            rep = '(' + str(x) + ') '
        else:
            rep = str(x) + ' '

        rep += str(k)

        for k in keys:
            x = self[k]

            if x == 1:
                rep += ' +'
            elif x == -1:
                rep += ' -'
            elif isinstance(x, Real):
                if x >= 0:
                    rep += ' + ' + str(x)
                else:
                    rep += ' - ' + str(-x) 
            elif type(x) is Add:
                rep += ' + (' + str(x) + ')'
            elif type(x) is Mul and x.args[0].is_real \
                 and x.args[0].is_number and x.args[0] < 0:
                rep += ' - ' + str(-x)
            else:
                rep += ' + ' + str(x)

            rep += ' ' + str(k)

        return rep

def conj(x):
    """Return conjugate of x."""
    return x.conjugate()

def conjx(x, *args):
    """Return the conjugate of x multiplied by arguments *args."""
    result = x.conjugate()

    for y in args:
        result *= y

    return result
    
def sqr(x):
    """Return the conjugate of x multiplied by x."""
    return x.conjugate() * x
