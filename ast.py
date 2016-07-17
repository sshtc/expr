# coding=utf-8
# author=veficos

import decimal


class Constant(object):
    def __init__(self, value):
        self.value = value

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __and__(self, other):
        return self.value and other.value

    def __or__(self, other):
        return self.value or other.value

    def __neg__(self):
        return -self.value;


class ArithmeticConstant(Constant):
    def __add__(self, other):
        return self.value + other.value

    def __sub__(self, other):
        return self.value - other.value

    def __mul__(self, other):
        return self.value * other.value

    def __truediv__ (self, other):
        return self.value / other.value

    def __mod__(self, other):
        return self.value % other.value


class IntegerConstant(ArithmeticConstant):
    def eval(self, env):
        return self.value

    def __repr__(self):
        return '(IntegerConstant: %d)' % self.value


class DecimalConstant(Constant):
    def eval(self, env):
        return self.value

    def __repr__(self):
        return '(DecimalConstant: %F)' % self.value


class BoolConstant(Constant):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return bool(self.value)

    def versa(self):
        return not self.value

    def __repr__(self):
        return '(BoolConstant: %F)' % self.value


class NilConstant(Constant):
    def eval(self, env):
        return None

    def __repr__(self):
        return '(NilConstant: None)'


class StringConstant(ArithmeticConstant):
    def eval(self, env):
        return self.value

    def __repr__(self):
        return '(StringConstant: %s)' % self.value


class Symbol(str):
    def eval(self, env):
        return env.get_object(str(self))

    def __repr__(self):
        return '(Symbol: %s)' % str(self)


class MemberObject(object):
    def __init__(self, obj, member):
        self.obj = obj
        self.member = member

    def eval(self, env):
        obj = self.obj.eval(env)
        subscript = self.member.eval(env).value
        try:
            if isinstance(obj, dict):
                return obj.get(subscript, NilConstant(None))
        except:
            pass
        return NilConstant(None)

    def __repr__(self):
        return '(MemberObject: %s.%s)' % (repr(self.obj), repr(self.member))


class FunctionCallObject(object):
    def __init__(self, function, args):
        self.function = function
        self.args = args

    def eval(self, env):
        function = self.function.eval(env)
        args = self.args.eval(env)
        return function(*args)

    def __repr__(self):
        return '(FunctionCallObject: %s(%s))' % (repr(self.function), repr(self.args))


class SubscriptObject(object):
    def __init__(self, obj, subscript):
        self.obj = obj
        self.subscript = subscript

    def eval(self, env):
        obj = self.obj.eval(env)
        subscript = self.subscript.eval(env)
        try:
            if isinstance(obj, list):
                return obj[subscript]
            elif isinstance(obj, dict):
                return obj.get(subscript, NilConstant(None))
        except:
            pass
        return NilConstant(None)

    def __repr__(self):
        return '(SubscriptObject: %s[%s])' % (repr(self.obj), repr(self.subscript))


class Member(object):
    def __init__(self, member):
        self.member = member

    def eval(self, env):
        return StringConstant(str(self.member))

    def __repr__(self):
        return "(Member: %s)" % str(self.member)


class FunctionArgs(object):
    def __init__(self, args):
        self.args = args

    def eval(self, env):
        return [x.eval(env) for x in self.args]

    def __repr__(self):
        return "(FunctionArgs: %s)" % ','.join([str(x) for x in self.args])


class Subscript(object):
    def __init__(self, subscript):
        self.subscript = subscript

    def eval(self, env):
        return self.subscript.eval(env)

    def __repr__(self):
        return '(Subscript: %s)' % repr(self.subscript)


class Negative(object):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return - self.value.eval(env)

    def __repr__(self):
        return '(Negative: -%s)' % repr(self.value)


class Not(object):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return not self.value.eval(env)

    def __repr__(self):
        return '(Not: !%s)' % repr(self.value)


class Binary(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class Multiply(Binary):
    def eval(self, env):
        return self.lhs.eval(env) * self.rhs.eval(env)

    def __repr__(self):
        return '(Multiply: %s*%s)' % (repr(self.lhs), repr(self.rhs))


class Divide(Binary):
    def eval(self, env):
        return self.lhs.eval(env) / self.rhs.eval(env)

    def __repr__(self):
        return '(Divide: %s/%s)' % (repr(self.lhs), repr(self.rhs))


class IntegerDivide(Binary):
    def eval(self, env):
        return self.lhs.eval(env) % self.rhs.eval(env)

    def __repr__(self):
        return '(IntegerDivide: %s%%%s)' % (repr(self.lhs), repr(self.rhs))


class Add(Binary):
    def eval(self, env):
        return self.lhs.eval(env) + self.rhs.eval(env)

    def __repr__(self):
        return '(Add: %s+%s)' % (repr(self.lhs), repr(self.rhs))


class Subtract(Binary):
    def eval(self, env):
        return self.lhs.eval(env) - self.rhs.eval(env)

    def __repr__(self):
        return '(Subtract: %s-%s)' % (repr(self.lhs), repr(self.rhs))


class LessOrEqual(Binary):
    def eval(self, env):
        return self.lhs.eval(env) <= self.rhs.eval(env)

    def __repr__(self):
        return '(LessOrEqual: %s<=%s)' % (repr(self.lhs), repr(self.rhs))


class GreaterOrEqual(Binary):
    def eval(self, env):
        return self.lhs.eval(env) >= self.rhs.eval(env)

    def __repr__(self):
        return '(GreaterOrEqual: %s>=%s)' % (repr(self.lhs), repr(self.rhs))


class LessThan(Binary):
    def eval(self, env):
        return self.lhs.eval(env) < self.rhs.eval(env)

    def __repr__(self):
        return '(LessThan: %s<%s)' % (repr(self.lhs), repr(self.rhs))


class GreaterThan(Binary):
    def eval(self, env):
        return self.lhs.eval(env) > self.rhs.eval(env)

    def __repr__(self):
        return '(GreaterThan: %s>%s)' % (repr(self.lhs), repr(self.rhs))


class Equal(Binary):
    def eval(self, env):
        print(type(self.lhs.eval(env)), type(self.rhs.eval(env)))
        return self.lhs.eval(env) == self.rhs.eval(env)

    def __repr__(self):
        return '(Equal: %s==%s)' % (repr(self.lhs), repr(self.rhs))


class Unequal(Binary):
    def eval(self, env):
        return self.lhs.eval(env) != self.rhs.eval(env)

    def __repr__(self):
        return '(Unequal: %s!=%s)' % (repr(self.lhs), repr(self.rhs))


class LogicalAnd(Binary):
    def eval(self, env):
        return self.lhs.eval(env) and self.rhs.eval(env)

    def __repr__(self):
        return '(LogicalAnd: %s&&%s)' % (repr(self.lhs), repr(self.rhs))


class LogicalOr(Binary):
    def eval(self, env):
        return self.lhs.eval(env) or self.rhs.eval(env)

    def __repr__(self):
        return '(LogicalOr: %s||%s)' % (repr(self.lhs), repr(self.rhs))