# coding=utf-8
# author=veficos

import decimal


class IntegerConstantNode(int):
    def eval(self, env):
        return self


class DecimalConstantNode(decimal.Decimal):
    def eval(self, env):
        return self


class BoolConstantNode(object):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return bool(self.value)

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

    def versa(self):
        return not self.value


class NilConstantNode(object):
    def __init__(self, value):
        pass

    def eval(self, env):
        return None


class StringConstantNode(str):
    def eval(self, env):
        return self


class SymbolNode(str):
    def eval(self, env):
        return self

class PostfixNode(object):
    def __init__(self, obj, other):
        self.obj = obj
        self.other = other

    def eval(self, env):
        return self.obj.eval(None), self.other


class NegativeNode(object):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value


class NotNode(object):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value


class BinaryNode(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class MultiplyNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class DivideNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class IntegerDivideNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class AddNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class SubtractNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class LessOrEqualNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class GreaterOrEqualNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class LessThanNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class GreaterThanNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class EqualNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class UnequalNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class LogicalAndNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs


class LogicalOrNode(BinaryNode):
    def eval(self, env):
        return self.lhs, self.rhs