# coding=utf-8
# author=左懒


import re
from pypeg2 import *


# Integer Constant
class DecimalConstant(Literal):
    grammar = re.compile(r'[1-9][0-9]*')

    def eval(self):
        return int(str(self), 10)


class OctalConstant(Literal):
    grammar = re.compile(r'0[0-7]*')

    def eval(self):
        return int(str(self), 8)


class HexadecimalConstant(Literal):
    grammar = re.compile(r'0[xX][0-9a-fA-F]+')

    def eval(self):
        return int(str(self), 16)

IntegerConstant = [
    HexadecimalConstant,
    OctalConstant,
    DecimalConstant,
]


# Float Constant
floating_suffix = r'[flFL]'

binary_exponent_part = r'([pP][+\-]?[0-9]+)'

hexadecimal_fractional_constant = r'([0-9a-fA-F]*\.[0-9a-fA-F]+)'

exponent_part = r'(E[+\-]?[0-9]+)'

fractional_constant = r'([0-9]*\.[0-9]+|[0-9]+\.)'


class HexadecimalFloatingConstant(Literal):
    grammar = re.compile(r'(0[xX]' + hexadecimal_fractional_constant +
                         binary_exponent_part + floating_suffix + r'?)|' +
                         r'(0[xX][0-9a-fA-F]+' + binary_exponent_part + floating_suffix + r'?)')

    def eval(self):
        return float(str(self))


class DecimalFloatingConstant(Literal):
    grammar = re.compile(r'(' + fractional_constant + exponent_part + r'?' +
                         floating_suffix + r'?)|' '([0-9]+' + exponent_part +
                         floating_suffix + r'?)')

    def eval(self):
        return float(str(self))

FloatingConstant = [
    HexadecimalFloatingConstant,
    DecimalFloatingConstant,
]


# Constant
Constant = [
    FloatingConstant,
    IntegerConstant,
]


# Primary expression
PrimaryExpression = [
    Constant,
]


class Multiply(List):
    def eval(self):
        return self[0].eval() * self[1].eval()


class Divide(List):
    def eval(self):
        return self[0].eval() / self[1].eval()


class IntegerDivide(List):
    def eval(self):
        return self[0].eval() % self[1].eval()

MultiplicativeExpression = [
    Multiply,
    Divide,
    IntegerDivide,
    PrimaryExpression
]

Multiply.grammar = PrimaryExpression, blank, "*", blank, MultiplicativeExpression
Divide.grammar = PrimaryExpression, blank, "/", blank, MultiplicativeExpression
IntegerDivide.grammar = PrimaryExpression, blank, "%", blank, MultiplicativeExpression


class Add(List):
    def eval(self):
        return self[0].eval() + self[1].eval()


class Subtract(List):
    def eval(self):
        return self[0].eval() + self[1].eval()

AdditiveExpression = [Add, Subtract, MultiplicativeExpression]
Add.grammar = MultiplicativeExpression, blank, "+", blank, AdditiveExpression
Subtract.grammar = MultiplicativeExpression, blank, "-", blank, AdditiveExpression


while True:
    text = input()
    ast = parse(text, AdditiveExpression)
    print(ast.eval())