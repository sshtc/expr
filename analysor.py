# coding=utf-8
# author=左懒


import decimal

from pypeg2 import *
from ast import *
from functools import reduce


def is_constant(expr):
    return any(map(lambda x: isinstance(expr, x), [
        IntegerConstantNode,
        DecimalConstantNode,
        BoolConstantNode,
        NilConstantNode,
        StringConstantNode,
    ]))


def binary_constant_folding(op, lhs, rhs):
    ops = {
        '+': lambda: lhs + rhs,
        '-': lambda: lhs - rhs,
        '*': lambda: lhs * rhs,
        '/': lambda: lhs / rhs,
        '%': lambda: lhs % rhs,

        '==': lambda: lhs == rhs,
        '!=': lambda: lhs != rhs,
        '>=': lambda: lhs >= rhs,
        '<=': lambda: lhs <= rhs,
        '>': lambda: lhs > rhs,
        '<': lambda: lhs < rhs,
        '||': lambda: lhs or rhs,
        '&&': lambda: lhs and rhs,
    }

    result = ops[op]()
    if isinstance(result, bool):
        return BoolConstantNode(result)
    elif any(map(lambda x: isinstance(result, x), [decimal.Decimal, float])):
        return DecimalConstantNode(result)
    elif isinstance(result, int):
        return IntegerConstantNode(result)
    elif isinstance(result, str):
        return StringConstantNode(result)


class Plain(object):
    def __init__(self, _name=None):
        if _name:
            self.name = Symbol(_name)

    def __repr__(self):
        try:
            self.name
        except AttributeError:
            return type(self).__name__ + "()"
        else:
            return type(self).__name__ + "(" + repr(self.name) + ")"

    def __eq__(self, other):
        if type(self) == type(other):
            try:
                self.name
            except AttributeError:
                return True
            else:
                return str(self.name) == str(other.name)
        else:
            return False


class DecConstantExpression(Literal):
    grammar = re.compile(r'[1-9][0-9]*')

    def to_value(self):
        return int(str(self), 10)

    def constant_folding(self):
        return IntegerConstantNode(self.to_value())


class OctConstantExpression(Literal):
    grammar = re.compile(r'0[0-7]*')

    def to_value(self):
        return int(str(self), 8)

    def constant_folding(self):
        return IntegerConstantNode(self.to_value())


class HexConstantExpression(Literal):
    grammar = re.compile(r'0[xX][0-9a-fA-F]+')

    def to_value(self):
        return int(str(self), 16)

    def constant_folding(self):
        return IntegerConstantNode(self.to_value())

__integer_constant_expression = [
    HexConstantExpression,
    OctConstantExpression,
    DecConstantExpression,
]


class DecimalConstantExpression(Literal):
    grammar = re.compile(r'[0-9]+\.[0-9]+')

    def to_value(self):
        return decimal.Decimal(str(self))

    def constant_folding(self):
        return DecimalConstantNode(self.to_value())

__decimal_constant_expression = [
    DecimalConstantExpression
]


class TrueConstantExpression(Literal):
    grammar = re.compile(r'true')

    def to_value(self):
        return True

    def constant_folding(self):
        return BoolConstantNode(self.to_value())


class FalseConstantExpression(Literal):
    grammar = re.compile(r'false')

    def to_value(self):
        return False

    def constant_folding(self):
        return BoolConstantNode(self.to_value())


class NilConstantExpression(Literal):
    grammar = re.compile(r'nil')

    def to_value(self):
        return None

    def constant_folding(self):
        return NilConstantNode(self.to_value())


class StringConstantExpression(Literal):
    ucn = r"(\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8})"

    hexadecimal_escape_sequence = r"(\\x[0-9a-fA-F]+)"

    octal_escape_sequence = r"(\\[0-7]{1,3})"

    simple_escape_sequence = r'(\\["' + r"'?\\abfnrtv])"

    escape_sequence = r"(" + simple_escape_sequence + r"|" \
                      + octal_escape_sequence + r"|" + hexadecimal_escape_sequence + r"|" + \
                      ucn + r")"

    s_char = r'([^"\\]|' + escape_sequence + r")"

    grammar = re.compile(r'((u8)|[uUL])?"' + s_char + r'*"')

    def to_value(self):
        return eval(str(self))

    def constant_folding(self):
        return StringConstantNode(self.to_value())

__constant_expression = [
    __decimal_constant_expression,
    __integer_constant_expression,
    StringConstantExpression,
    TrueConstantExpression,
    FalseConstantExpression,
    NilConstantExpression,
]


class ParenthesesExpression(List):
    def constant_folding(self):
        return self[0].constant_folding()


class IdentifierExpression(Literal):
    ucn = r"(\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8})"
    grammar = re.compile(r"([a-zA-Z_]|" + ucn + r")([0-9a-zA-Z_]|" + ucn + r")*")

    def to_value(self):
        return str(self)

    def constant_folding(self):
        return SymbolNode(self.to_value())

__primary_expression = [
    __constant_expression,
    ParenthesesExpression,
    IdentifierExpression,
]


class MemberExpression(Plain):
    grammar = '.', name()

    def constant_folding(self):
        return SymbolNode(self.name)


class FunctionCallExpression(List):
    def constant_folding(self):
        return list(map(lambda x: x.constant_folding(), self))


class SubscriptExpression(List):
    def constant_folding(self):
        return self[0].constant_folding()

_postfix = [
    MemberExpression,
    FunctionCallExpression,
    SubscriptExpression,
]


class PostfixExpression(List):
    grammar = [IdentifierExpression], some(_postfix)

    def constant_folding(self):
        return reduce(lambda x, y: PostfixNode(x, y), map(lambda x: x.constant_folding(), self))

__postfix_expression = [
    PostfixExpression,
    __primary_expression
]


class NegativeExpression(List):
    def constant_folding(self):
        value = self[0].constant_folding()
        if isinstance(value, IntegerConstantNode):
            return IntegerConstantNode(-value)
        elif isinstance(value, DecimalConstantNode):
            return DecimalConstantNode(-value)
        return NegativeNode(self[0])


class NotExpression(List):
    def constant_folding(self):
        value = self[0].constant_folding()
        if any(map(lambda x: isinstance(value, x), [
            BoolConstantNode,
        ])):
            return BoolConstantNode(value.versa())
        return NotNode(self[0])

__unary_expression = [
    __postfix_expression,
    NegativeExpression,
    NotExpression,
]

NegativeExpression.grammar = "-", __postfix_expression
NotExpression.grammar = "!", __postfix_expression


class MultiplyExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('*', lhs, rhs)
        return MultiplyNode(lhs, rhs)


class DivideExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('/', lhs, rhs)
        return DivideNode(lhs, rhs)


class IntegerDivideExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('%', lhs, rhs)
        return IntegerDivideNode(lhs, rhs)

__multiplicative_expression = [
    MultiplyExpression,
    DivideExpression,
    IntegerDivideExpression,
    __unary_expression
]

MultiplyExpression.grammar = __unary_expression, blank, "*", blank, __multiplicative_expression
DivideExpression.grammar = __unary_expression, blank, "/", blank, __multiplicative_expression
IntegerDivideExpression.grammar = __unary_expression, blank, "%", blank, __multiplicative_expression


class AddExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('+', lhs, rhs)
        return AddNode(lhs, rhs)


class SubtractExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('-', lhs, rhs)
        return SubtractNode(lhs, rhs)

__additive_expression = [AddExpression, SubtractExpression, __multiplicative_expression]
AddExpression.grammar = __multiplicative_expression, blank, "+", blank, __additive_expression
SubtractExpression.grammar = __multiplicative_expression, blank, "-", blank, __additive_expression


class LessOrEqualExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('<=', lhs, rhs)
        return LessOrEqualNode(lhs, rhs)


class GreaterOrEqualExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('>=', lhs, rhs)
        return GreaterOrEqualNode(lhs, rhs)


class LessThanExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        print('less than')
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('<', lhs, rhs)
        return LessThanNode(lhs, rhs)


class GreaterThanExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('>', lhs, rhs)
        return GreaterThanNode(lhs, rhs)

__relational_expression = [
    LessOrEqualExpression,
    GreaterOrEqualExpression,
    LessThanExpression,
    GreaterThanExpression,
    __additive_expression
]

LessOrEqualExpression.grammar = __additive_expression, blank, "<=", blank, __relational_expression
GreaterOrEqualExpression.grammar = __additive_expression, blank, ">=", blank, __relational_expression
LessThanExpression.grammar = __additive_expression, blank, "<", blank, __relational_expression
GreaterThanExpression.grammar = __additive_expression, blank, ">", blank, __relational_expression


class EqualExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('==', lhs, rhs)
        return EqualNode(lhs, rhs)


class UnequalExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('!=', lhs, rhs)
        return LessThanNode(lhs, rhs)

__equality_expression = [
    EqualExpression,
    UnequalExpression,
    __relational_expression
]

EqualExpression.grammar = __relational_expression, blank, "==", blank, __equality_expression
UnequalExpression.grammar = __relational_expression, blank, "!=", blank, __equality_expression


class LogicalAndExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('&&', lhs, rhs)
        return LogicalAndNode(lhs, rhs)

__logical_and_expression = [LogicalAndExpression, __equality_expression]
LogicalAndExpression.grammar = __equality_expression, blank, "&&", blank, __logical_and_expression


class LogicalOrExpression(List):
    def constant_folding(self):
        lhs = self[0].constant_folding()
        rhs = self[1].constant_folding()
        if all([is_constant(lhs), is_constant(rhs)]):
            return binary_constant_folding('||', lhs, rhs)
        return LogicalOrNode(lhs, rhs)

__logical_or_expression = [LogicalOrExpression, __logical_and_expression]
LogicalOrExpression.grammar = __logical_and_expression, blank, "||", blank, __logical_or_expression

Expression = __logical_or_expression

ParenthesesExpression.grammar = '(', csl(Expression), ")"
SubscriptExpression.grammar = "[", Expression, "]"
FunctionCallExpression.grammar = "(", optional(csl(Expression)), ")"


class Parser(object):
    @staticmethod
    def parse(text):
        return parse(text, Expression)

while True:
    text = input()
    ast = Parser.parse(text)
    print(ast)
    print(type(ast.constant_folding()), ": ", ast.constant_folding().eval(None))