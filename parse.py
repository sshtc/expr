# coding=utf-8
# author=veficos


import decimal
import pypeg2
import re

from ast import *
from functools import reduce


def is_constant(expr):
    return any(map(lambda x: isinstance(expr, x), [
        IntegerConstant,
        DecimalConstant,
        BoolConstant,
        NilConstant,
        StringConstant,
    ]))


def is_object(expr):
    return any(map(lambda x: isinstance(expr, x), [
        Symbol,
        FunctionCallObject,
        Subscript,
        MemberObject,
    ]))


def is_binary_expression(expr):
    return any(map(lambda x: isinstance(expr, x), [
        MultiplyExpression,
        DivideExpression,
        IntegerDivideExpression,
        AddExpression,
        SubtractExpression,
        LessOrEqualExpression,
        GreaterOrEqualExpression,
        LessThanExpression,
        GreaterThanExpression,
        EqualExpression,
        UnequalExpression,
        LogicalAndExpression,
        LogicalOrExpression,
    ]))


def repair_binary_expression(lhs, rhs, expr, expr_classes):
    for expr_class in expr_classes:
        if isinstance(rhs, expr_class):
            return repair_binary_expression(expr(lhs, rhs[0]), rhs[1], expr_class, expr_classes)
    return expr(lhs, rhs)


def binary_abstract_syntax_tree(op, lhs, rhs):
    ops = {
        '+': lambda: lhs.value + rhs.value,
        '-': lambda: lhs.value - rhs.value,
        '*': lambda: lhs.value * rhs.value,
        '/': lambda: lhs.value / rhs.value,
        '%': lambda: lhs.value % rhs.value,

        '==': lambda: lhs.value == rhs.value,
        '!=': lambda: lhs.value != rhs.value,
        '>=': lambda: lhs.value.value >= rhs.value,
        '<=': lambda: lhs.value <= rhs.value,
        '>': lambda: lhs.value > rhs.value,
        '<': lambda: lhs.value < rhs.value,
        '||': lambda: lhs.value or rhs.value,
        '&&': lambda: lhs.value and rhs.value,
    }

    result = ops[op]()
    if isinstance(result, bool):
        return BoolConstant(result)
    elif any(map(lambda x: isinstance(result, x), [decimal.Decimal, float])):
        return DecimalConstant(result)
    elif isinstance(result, int):
        return IntegerConstant(result)
    elif isinstance(result, str):
        return StringConstant(result)
    return NilConstant(None)


class Plain(object):
    def __init__(self, _name=None):
        if _name:
            self.name = pypeg2.Symbol(_name)

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


class DecConstantExpression(pypeg2.Literal):
    grammar = re.compile(r'[1-9][0-9]*')

    def to_value(self):
        return int(str(self), 10)

    def abstract_syntax_tree(self):
        return IntegerConstant(self.to_value())


class OctConstantExpression(pypeg2.Literal):
    grammar = re.compile(r'0[0-7]*')

    def to_value(self):
        return int(str(self), 8)

    def abstract_syntax_tree(self):
        return IntegerConstant(self.to_value())


class HexConstantExpression(pypeg2.Literal):
    grammar = re.compile(r'0[xX][0-9a-fA-F]+')

    def to_value(self):
        return int(str(self), 16)

    def abstract_syntax_tree(self):
        return IntegerConstant(self.to_value())

__integer_constant_expression = [
    HexConstantExpression,
    OctConstantExpression,
    DecConstantExpression,
]


class DecimalConstantExpression(pypeg2.Literal):
    grammar = re.compile(r'[0-9]+\.[0-9]+')

    def to_value(self):
        return decimal.Decimal(str(self))

    def abstract_syntax_tree(self):
        return DecimalConstant(self.to_value())

__decimal_constant_expression = [
    DecimalConstantExpression
]


class TrueConstantExpression(pypeg2.Literal):
    grammar = re.compile(r'true')

    def to_value(self):
        return True

    def abstract_syntax_tree(self):
        return BoolConstant(self.to_value())


class FalseConstantExpression(pypeg2.Literal):
    grammar = re.compile(r'false')

    def to_value(self):
        return False

    def abstract_syntax_tree(self):
        return BoolConstant(self.to_value())


class NilConstantExpression(pypeg2.Literal):
    grammar = re.compile(r'nil')

    def to_value(self):
        return None

    def abstract_syntax_tree(self):
        return NilConstant(None)


class StringConstantExpression(pypeg2.Literal):
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

    def abstract_syntax_tree(self):
        return StringConstant(self.to_value())

__constant_expression = [
    __decimal_constant_expression,
    __integer_constant_expression,
    StringConstantExpression,
    TrueConstantExpression,
    FalseConstantExpression,
    NilConstantExpression,
]


class ParenthesesExpression(pypeg2.List):
    def abstract_syntax_tree(self):
        return self[0].abstract_syntax_tree()


class IdentifierExpression(pypeg2.Literal):
    ucn = r"(\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8})"
    grammar = re.compile(r"([a-zA-Z_]|" + ucn + r")([0-9a-zA-Z_]|" + ucn + r")*")

    def to_value(self):
        return str(self)

    def abstract_syntax_tree(self):
        return Symbol(self.to_value())

__primary_expression = [
    __constant_expression,
    ParenthesesExpression,
    IdentifierExpression,
]


class MemberExpression(Plain):
    grammar = '.', pypeg2.name()

    def abstract_syntax_tree(self):
        return Member(self.name)


class FunctionCallExpression(pypeg2.List):
    def abstract_syntax_tree(self):
        return FunctionArgs(list(map(lambda x: x.abstract_syntax_tree(), self)))


class SubscriptExpression(pypeg2.List):
    def abstract_syntax_tree(self):
        return Subscript(self[0].abstract_syntax_tree())

_postfix = [
    MemberExpression,
    FunctionCallExpression,
    SubscriptExpression,
]


class PostfixExpression(pypeg2.List):
    grammar = [IdentifierExpression], pypeg2.some(_postfix)

    def abstract_syntax_tree(self):
        def error():
            raise Exception('undefined object')

        return reduce(lambda x, y:
                      MemberObject(x, y) if any(map(lambda t: isinstance(y, t), [MemberObject, Member])) else \
                      FunctionCallObject(x, y) if any(map(lambda t: isinstance(y, t), [FunctionCallObject, FunctionArgs])) else \
                      SubscriptObject(x, y) if any(map(lambda t: isinstance(y, t), [SubscriptObject, Subscript])) else error(),
                      map(lambda x: x.abstract_syntax_tree(), self))

__postfix_expression = [
    PostfixExpression,
    __primary_expression
]


class NegativeExpression(pypeg2.List):
    def abstract_syntax_tree(self):
        value = self[0].abstract_syntax_tree()
        if isinstance(value, IntegerConstant):
            return IntegerConstant(-value)
        elif isinstance(value, DecimalConstant):
            return DecimalConstant(-value)
        return Negative(value)


class NotExpression(pypeg2.List):
    def abstract_syntax_tree(self):
        value = self[0].abstract_syntax_tree()
        if any(map(lambda x: isinstance(value, x), [
            BoolConstant,
        ])):
            return BoolConstant(value.versa())
        return Not(value)

__unary_expression = [
    __postfix_expression,
    NegativeExpression,
    NotExpression,
]

NegativeExpression.grammar = "-", __postfix_expression
NotExpression.grammar = "!", __postfix_expression


class MultiplyExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], MultiplyExpression, [DivideExpression, IntegerDivideExpression])

    def abstract_syntax_tree(self):
        return Multiply(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())


class DivideExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], DivideExpression, [MultiplyExpression, IntegerDivideExpression])

    def abstract_syntax_tree(self):
        return Divide(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())


class IntegerDivideExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], IntegerDivideExpression, [MultiplyExpression, DivideExpression])
        
    def abstract_syntax_tree(self):
        return IntegerDivide(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())

__multiplicative_expression = [
    MultiplyExpression,
    DivideExpression,
    IntegerDivideExpression,
    __unary_expression
]

MultiplyExpression.grammar = __unary_expression, pypeg2.blank, "*", pypeg2.blank, __multiplicative_expression
DivideExpression.grammar = __unary_expression, pypeg2.blank, "/", pypeg2.blank, __multiplicative_expression
IntegerDivideExpression.grammar = __unary_expression, pypeg2.blank, "%", pypeg2.blank, __multiplicative_expression


class AddExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], AddExpression, [SubtractExpression])

    def abstract_syntax_tree(self):
        return Add(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())


class SubtractExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], AddExpression, [AddExpression])

    def abstract_syntax_tree(self):
        return Subtract(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())

__additive_expression = [AddExpression, SubtractExpression, __multiplicative_expression]
AddExpression.grammar = __multiplicative_expression, pypeg2.blank, "+", pypeg2.blank, __additive_expression
SubtractExpression.grammar = __multiplicative_expression, pypeg2.blank, "-", pypeg2.blank, __additive_expression

class LessOrEqualExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], [GreaterOrEqualExpression, LessThanExpression, LessThanExpression])

    def abstract_syntax_tree(self):
        return LessOrEqual(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())


class GreaterOrEqualExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], [LessOrEqualExpression, LessThanExpression, LessThanExpression])

    def abstract_syntax_tree(self):
        return GreaterOrEqual(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())


class LessThanExpression(pypeg2.List):
    def repair(self):
            return repair_binary_expression(self[0], self[1], [LessOrEqualExpression, GreaterOrEqualExpression, GreaterThanExpression])

    def abstract_syntax_tree(self):
        return LessThan(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())


class GreaterThanExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], [LessOrEqualExpression, GreaterOrEqualExpression, LessThanExpression])

    def abstract_syntax_tree(self):
        return GreaterThan(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())

__relational_expression = [
    LessOrEqualExpression,
    GreaterOrEqualExpression,
    LessThanExpression,
    GreaterThanExpression,
    __additive_expression
]

LessOrEqualExpression.grammar = __additive_expression, pypeg2.blank, "<=", pypeg2.blank, __relational_expression
GreaterOrEqualExpression.grammar = __additive_expression, pypeg2.blank, ">=", pypeg2.blank, __relational_expression
LessThanExpression.grammar = __additive_expression, pypeg2.blank, "<", pypeg2.blank, __relational_expression
GreaterThanExpression.grammar = __additive_expression, pypeg2.blank, ">", pypeg2.blank, __relational_expression


class EqualExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], EqualExpression, [UnequalExpression])

    def abstract_syntax_tree(self):
        return Equal(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())


class UnequalExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], UnequalExpression, [EqualExpression])

    def abstract_syntax_tree(self):
        return Unequal(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())

__equality_expression = [
    EqualExpression,
    UnequalExpression,
    __relational_expression
]

EqualExpression.grammar = __relational_expression, pypeg2.blank, "==", pypeg2.blank, __equality_expression
UnequalExpression.grammar = __relational_expression, pypeg2.blank, "!=", pypeg2.blank, __equality_expression


class LogicalAndExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], LogicalAndExpression, [LogicalOrExpression])

    def abstract_syntax_tree(self):
        return LogicalAnd(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())

__logical_and_expression = [LogicalAndExpression, __equality_expression]
LogicalAndExpression.grammar = __equality_expression, pypeg2.blank, "&&", pypeg2.blank, __logical_and_expression


class LogicalOrExpression(pypeg2.List):
    def repair(self):
        return repair_binary_expression(self[0], self[1], LogicalOrExpression, [LogicalAndExpression])

    def abstract_syntax_tree(self):
        return LogicalOr(self[0].abstract_syntax_tree(), self[1].abstract_syntax_tree())

__logical_or_expression = [LogicalOrExpression, __logical_and_expression]
LogicalOrExpression.grammar = __logical_and_expression, pypeg2.blank, "||", pypeg2.blank, __logical_or_expression

Expression = __logical_or_expression

ParenthesesExpression.grammar = '(', pypeg2.csl(Expression), ")"
SubscriptExpression.grammar = "[", Expression, "]"
FunctionCallExpression.grammar = "(", pypeg2.optional(pypeg2.csl(Expression)), ")"


class Parser(object):
    @staticmethod
    def parse(text):
        expr = pypeg2.parse(text, Expression)
        if is_binary_expression(expr):
            return expr.repair()
        return expr