# coding=utf-8
# author=veficos

import decimal


class Constant(object):
    def __init__(self, value):
        self.value = value


class IntegerConstant(Constant):
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


class StringConstant(Constant):
    def eval(self, env):
        return self.value

    def __repr__(self):
        return '(StringConstant: %s)' % self.value


class Symbol(str):
    def eval(self, env):
        return env.get_object(str(self))

    def __repr__(self):
        return '(Symbol: %s)' % str(self)


class Member(object):
    def __init__(self, obj, member):
        self.obj = obj
        self.member = member

    def eval(self, env):
        obj = self.obj.eval(env)
        subscript = self.member
        try:
            if isinstance(obj, dict):
                return obj.get(subscript, NilConstant(None))
        except:
            pass
        return NilConstant(None)

    def __repr__(self):
        return '(Member: %s.%s)' % (repr(self.obj), repr(self.member))


class FunctionCall(object):
    def __init__(self, function, args):
        self.function = function
        self.args = args

    def eval(self, env):
        function = self.function.eval(env)
        args = [x.eval(env) for x in self.args]

        return function(*args)

    def __repr__(self):
        return '(FunctionCall: %s(%s))' % (repr(self.function), repr(self.args))


class Subscript(object):
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
        return '(Subscript: %s[%s])' % (repr(self.obj), repr(self.subscript))


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
        return self.lhs.eval(env) == self.rhs.eval(env)

    def __repr__(self):
        return '(Equal: %s==%s)' % (repr(self.lhs), repr(self.rhs))


class UnEqual(Binary):
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


class If(object):
    def __init__(self, yes, condition, no):
        self.yes = yes
        self.condition = condition
        self.no = no

    def eval(self, env):
        condition = self.condition.eval(env)
        if condition:
            return self.yes.eval(env)
        return self.no.eval(env)

    def __repr__(self):
        return '(If: %s if %s else %s)' % (repr(self.yes), repr(self.condition), repr(self.no))