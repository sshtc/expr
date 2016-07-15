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


class IntegerConstantNode(ArithmeticConstant):
    def eval(self, env):
        return self.value

    def __repr__(self):
        return '(IntegerConstantNode: %d)' % self.value


class DecimalConstantNode(Constant):
    def eval(self, env):
        return self.value

    def __repr__(self):
        return '(DecimalConstantNode: %F)' % self.value


class BoolConstantNode(Constant):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return bool(self.value)

    def versa(self):
        return not self.value

    def __repr__(self):
        return '(BoolConstantNode: %F)' % self.value


class NilConstantNode(Constant):
    def eval(self, env):
        return None

    def __repr__(self):
        return '(NilConstantNode: None)'


class StringConstantNode(ArithmeticConstant):
    def eval(self, env):
        return self.value

    def __repr__(self):
        return '(StringConstantNode: %s)' % self.value


class SymbolNode(str):
    def eval(self, env):
        return env.get_object(str(self))

    def __repr__(self):
        return '(SymbolNode: %s)' % str(self)


class MemberObjectNode(object):
    def __init__(self, obj, member):
        self.obj = obj
        self.member = member

    def eval(self, env):
        obj = self.obj.eval(env)
        subscript = self.member.eval(env).value
        try:
            if isinstance(obj, dict):
                return obj.get(subscript, NilConstantNode(None))
        except:
            pass
        return NilConstantNode(None)

    def __repr__(self):
        return '(MemberObjectNode: %s.%s)' % (repr(self.obj), repr(self.member))


class FunctionCallObjectNode(object):
    def __init__(self, function, args):
        self.function = function
        self.args = args

    def eval(self, env):
        function = self.function.eval(env)
        args = self.args.eval(env)
        return function(*args)

    def __repr__(self):
        return '(FunctionCallObjectNode: %s(%s))' % (repr(self.function), repr(self.args))


class SubscriptObjectNode(object):
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
                return obj.get(subscript, NilConstantNode(None))
        except:
            pass
        return NilConstantNode(None)

    def __repr__(self):
        return '(SubscriptObjectNode: %s[%s])' % (repr(self.obj), repr(self.subscript))


class MemberNode(object):
    def __init__(self, member):
        self.member = member

    def eval(self, env):
        return StringConstantNode(str(self.member))

    def __repr__(self):
        return "(MemberNode: %s)" % str(self.member)


class FunctionArgsNode(object):
    def __init__(self, args):
        self.args = args

    def eval(self, env):
        return [x.eval(env) for x in self.args]

    def __repr__(self):
        return ','.join([str(x) for x in self.args])


class SubscriptNode(object):
    def __init__(self, subscript):
        self.subscript = subscript

    def eval(self, env):
        return self.subscript.eval(env)

    def __repr__(self):
        return '(SubscriptNode: %s)' % repr(self.subscript)


class NegativeNode(object):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return - self.value.eval(env)

    def __repr__(self):
        return '(NegativeNode: -%s)' % repr(self.value)


class NotNode(object):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return not self.value.eval(env)

    def __repr__(self):
        return '(NegativeNode: !%s)' % repr(self.value)


class BinaryNode(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class MultiplyNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) * self.rhs.eval(env)

    def __repr__(self):
        return '(MultiplyNode: %s*%s)' % (repr(self.lhs), repr(self.rhs))


class DivideNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) / self.rhs.eval(env)

    def __repr__(self):
        return '(DivideNode: %s/%s)' % (repr(self.lhs), repr(self.rhs))


class IntegerDivideNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) % self.rhs.eval(env)

    def __repr__(self):
        return '(IntegerDivideNode: %s%%%s)' % (repr(self.lhs), repr(self.rhs))


class AddNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) + self.rhs.eval(env)

    def __repr__(self):
        return '(AddNode: %s+%s)' % (repr(self.lhs), repr(self.rhs))


class SubtractNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) - self.rhs.eval(env)

    def __repr__(self):
        return '(SubtractNode: %s-%s)' % (repr(self.lhs), repr(self.rhs))


class LessOrEqualNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) <= self.rhs.eval(env)

    def __repr__(self):
        return '(LessOrEqualNode: %s<=%s)' % (repr(self.lhs), repr(self.rhs))


class GreaterOrEqualNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) >= self.rhs.eval(env)

    def __repr__(self):
        return '(GreaterOrEqualNode: %s>=%s)' % (repr(self.lhs), repr(self.rhs))


class LessThanNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) < self.rhs.eval(env)

    def __repr__(self):
        return '(LessThanNode: %s<%s)' % (repr(self.lhs), repr(self.rhs))


class GreaterThanNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) > self.rhs.eval(env)

    def __repr__(self):
        return '(GreaterThanNode: %s>%s)' % (repr(self.lhs), repr(self.rhs))


class EqualNode(BinaryNode):
    def eval(self, env):
        print(type(self.lhs.eval(env)), type(self.rhs.eval(env)))
        return self.lhs.eval(env) == self.rhs.eval(env)

    def __repr__(self):
        return '(EqualNode: %s==%s)' % (repr(self.lhs), repr(self.rhs))


class UnequalNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) != self.rhs.eval(env)

    def __repr__(self):
        return '(UnequalNode: %s!=%s)' % (repr(self.lhs), repr(self.rhs))


class LogicalAndNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) and self.rhs.eval(env)

    def __repr__(self):
        return '(LogicalAndNode: %s&&%s)' % (repr(self.lhs), repr(self.rhs))


class LogicalOrNode(BinaryNode):
    def eval(self, env):
        return self.lhs.eval(env) or self.rhs.eval(env)

    def __repr__(self):
        return '(LogicalOrNode: %s||%s)' % (repr(self.lhs), repr(self.rhs))