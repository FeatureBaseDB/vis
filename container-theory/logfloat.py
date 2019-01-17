import math

class Log10Float(object):
    """
    Numerical type, stores the log10 exponent of the number.
    Handles basic arithmetic between this type and [int, long, float].

    Instantiate:
    Log10Float(234)  # create a Log10Float representing the *value* 123
    Log10Float(exp=2.1)  # create a Log10Float representing the *exponent* 2.1, 10 ** 2.1 = 125.8...
    """
    precision = 10  # operations maintain this many digits of precision

    def __init__(self, value=0, exp=None):
        if exp:
            self.exp = float(exp)
        else:
            self.exp = math.log10(value)

    def _handle_add_sub_special_cases(self, x, y):
        res = None
        if x == -np.inf and y == -np.inf:
            # handle 0+0 case
            res = -np.inf

        if x > y:
            # enforce y >= x
            x, y = y, x

        if y - x > self.precision:
            # don't do any math if not necessary
            res = y

        return x, y, res

    def _get_other_exp(self, other):
        if type(other) == Log10Float:
            other_exp = other.exp
        elif type(other) in [int, long, float]:
            other_exp = math.log10(other)
        return other_exp

    def __mul__(self, other):
        other_exp = self._get_other_exp(other)
        new_exp = self.exp + other_exp
        return Log10Float(exp=new_exp)

    def __div__(self, other):
        other_exp = self._get_other_exp(other)
        new_exp = self.exp - other_exp
        return Log10Float(exp=new_exp)

    def __add__(self, other):
        """
        given x, y, y >= x, compute z where 10^z = 10^x + 10^y
        z = log(10^x + 10^y)
        z = log(10^y(1 + 10^(x-y)))
        z = y + log(1 + 10^(x-y))
        """
        other_exp = self._get_other_exp(other)
        x, y, res = self._handle_add_sub_special_cases(self.exp, other_exp)
        if res:
            return res
        new_exp = y + math.log10(1 + 10 ** (x-y))
        return Log10Float(exp=new_exp)

    def __sub__(self, other):
        """
        givem x, y, y >= x, compute z where 10^z = 10^x - 10^y
        z = y + log(1 - 10^(x-y))
        """
        # needs to handle negative values, which
        # means including a sign variable
        # not necessary here.
        raise NotImplementedError

    def _log10float_eq(self, other):
        raise NotImplementedError

    def _primitive_eq(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        if type(other) == Log10Float:
            return self._log10float_eq(other)
        elif type(other) in [int, float]:
            return self._primitive_eq(other)

    def __repr__(self):
        return '%fE%d' % (10 ** (self.exp - int(self.exp)), int(self.exp))


def fcmp(x, y):
    """float compare, in place of equality"""
    return x == y


def test_log():
    x = 12345.0
    y = 23456.0
    lx = Log10Float(12345)
    ly = Log10Float(23456)
    assert(fcmp((lx*ly).exp, math.log10(x*y)))
    assert(fcmp((lx/ly).exp, math.log10(x/y)))
    assert(fcmp((lx+ly).exp, math.log10(x+y)))
    assert(fcmp((lx-ly).exp, math.log10(x-y)))

    a = x + y
    b = x * y
    c = x - y
    d = x / y
    la = lx + ly
    lb = lx * ly
    lc = lx - ly
    ld = lx / ly
    print(x, y, a, b, c, d)
    print(lx, ly, la, lb, lc, ld)

print('asdf')
test_log()