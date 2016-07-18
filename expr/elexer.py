# coding=utf-8
# author=utf-8

import re
import decimal


class LexerError(Exception):
    pass


class Token:
    IntegerConstant = 1
    DecimalConstant = 2
    TrueConstant = 3
    FalseConstant = 4
    NilConstant = 5
    StringConstant = 6
    Identifier = 7
    LeftParentheses = 8
    RightParentheses = 9
    LeftBracket = 10
    RightBracket = 11
    Dot = 12
    Add = 13
    Sub = 14
    Mul = 15
    Div = 16
    Mod = 17
    And = 18
    Or = 19
    Not = 20
    Eq = 21
    Neq = 22
    Lt = 23
    Leq = 24
    Gt = 25
    Geq = 26
    Comma = 27
    If = 28
    Else = 29
    Eof = 30


class Lexer(object):
    def __init__(self, text):
        self.text = text

    def __next_parse(self, regex, token, wrapper, continuation):
        if not self.text:
            return Token.Eof, None

        r = re.compile(regex)
        g = r.match(self.text)
        if g:
            start, end = g.span()
            text = self.text[start:end]
            self.text = self.text[end:]
            return token, wrapper(text)
        return continuation(False)

    def __peek_parse(self, regex, token, wrapper, continuation):
        if not self.text:
            return Token.Eof, None

        r = re.compile(regex)
        g = r.match(self.text)
        if g:
            start, end = g.span()
            text = self.text[start:end]
            return token, wrapper(text)
        return continuation(True)

    def __parse(self, peek, regex, token, wrapper, continuation):
        return self.__peek_parse(regex, token, wrapper, continuation) \
            if peek else self.__next_parse(regex, token, wrapper, continuation)

    def __parse_hex_integer(self, peek):
        return self.__parse(peek, r'0[xX][0-9a-fA-F]+', Token.IntegerConstant, lambda x: int(x, 16), self.__parse_decimal)

    def __parse_decimal(self, peek):
        return self.__parse(peek, r'[0-9]+\.[0-9]+', Token.DecimalConstant, lambda x: decimal.Decimal(x), self.__parse_oct_integer)

    def __parse_oct_integer(self, peek):
        return self.__parse(peek, r'0[0-7]*', Token.IntegerConstant, lambda x: int(x, 8), self.__parse_dec_integer)

    def __parse_dec_integer(self, peek):
        return self.__parse(peek, r'[1-9][0-9]*', Token.IntegerConstant, lambda x: int(x, 10), self.__parse_true)

    def __parse_true(self, peek):
        return self.__parse(peek, r'true', Token.TrueConstant, lambda x: True, self.__parse_false)

    def __parse_false(self, peek):
        return self.__parse(peek, r'false', Token.FalseConstant, lambda x: False, self.__parse_nil)

    def __parse_nil(self, peek):
        return self.__parse(peek, r'nil', Token.NilConstant, lambda x: None, self.__parse_string)

    def __parse_string(self, peek):
        ucn = r"(\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8})"

        hexadecimal_escape_sequence = r"(\\x[0-9a-fA-F]+)"

        octal_escape_sequence = r"(\\[0-7]{1,3})"

        simple_escape_sequence = r'(\\["' + r"'?\\abfnrtv])"

        escape_sequence = r"(" + simple_escape_sequence + r"|" \
                          + octal_escape_sequence + r"|" + hexadecimal_escape_sequence + r"|" + \
                          ucn + r")"

        s_char = r'([^"\\]|' + escape_sequence + r")"

        return self.__parse(peek, r'((u8)|[uUL])?"' + s_char + r'*"', Token.StringConstant, lambda x: x[1:-1], self.__parse_if)

    def __parse_if(self, peek):
        return self.__parse(peek, r'if', Token.If, lambda x: x, self.__parse_else)

    def __parse_else(self, peek):
        return self.__parse(peek, r'else', Token.Else, lambda x: x, self.__parse_identifier)

    def __parse_identifier(self, peek):
        ucn = r"(\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8})"
        return self.__parse(peek, r"([a-zA-Z_]|" + ucn + r")([0-9a-zA-Z_]|" + ucn + r")*", Token.Identifier, lambda x: x,
                          self.__parse_left_parentheses)

    def __parse_left_parentheses(self, peek):
        return self.__parse(peek, r"\(", Token.LeftParentheses, lambda x: x, self.__parse_right_parentheses)

    def __parse_right_parentheses(self, peek):
        return self.__parse(peek, r'\)', Token.RightParentheses, lambda x: x, self.__parse_left_bracket)

    def __parse_left_bracket(self, peek):
        return self.__parse(peek, r'\[', Token.LeftBracket, lambda x: x, self.__parse_right_bracket)

    def __parse_right_bracket(self, peek):
        return self.__parse(peek, r'\]', Token.RightBracket, lambda x: x, self.__parse_dot)

    def __parse_dot(self, peek):
        return self.__parse(peek, r'\.', Token.Dot, lambda x: x, self.__parse_add)

    def __parse_add(self, peek):
        return self.__parse(peek, r'\+', Token.Add, lambda x: x, self.__parse_sub)

    def __parse_sub(self, peek):
        return self.__parse(peek, r'-', Token.Sub, lambda x: x, self.__parse_mul)

    def __parse_mul(self, peek):
        return self.__parse(peek, r'\*', Token.Mul, lambda x: x, self.__parse_div)

    def __parse_div(self, peek):
        return self.__parse(peek, r'/', Token.Div, lambda x: x, self.__parse_mod)

    def __parse_mod(self, peek):
        return self.__parse(peek, r'%', Token.Mod, lambda x: x, self.__parse_and)

    def __parse_and(self, peek):
        return self.__parse(peek, r'&&', Token.Mod, lambda x: x, self.__parse_or)

    def __parse_or(self, peek):
        return self.__parse(peek, r'\|\|', Token.Or, lambda x: x, self.__parse_not)

    def __parse_not(self, peek):
        return self.__parse(peek, r'!', Token.Not, lambda x: x, self.__parse_eq)

    def __parse_eq(self, peek):
        return self.__parse(peek, r'==', Token.Eq, lambda x: x, self.__parse_neq)

    def __parse_neq(self, peek):
        return self.__parse(peek, r'!=', Token.Neq, lambda x: x, self.__parse_lt)

    def __parse_lt(self, peek):
        return self.__parse(peek, r'<', Token.Lt, lambda x: x, self.__parse_leq)

    def __parse_leq(self, peek):
        return self.__parse(peek, r'<=', Token.Leq, lambda x: x, self.__parse_gt)

    def __parse_gt(self, peek):
        return self.__parse(peek, r'>', Token.Leq, lambda x: x, self.__parse_geq)

    def __parse_geq(self, peek):
        return self.__parse(peek, r'>=', Token.Geq, lambda x: x, self.__parse_comma)

    def __parse_comma(self, peek):
        return self.__parse(peek, r',', Token.Comma, lambda x: x, self.__parse_blank)

    def __parse_blank(self, peek):
        if not self.text:
            return Token.Eof, None

        r = re.compile(r'\s')
        g = r.match(self.text)
        if g:
            start, end = g.span()
            self.text = self.text[end:]
            return self.__parse_hex_integer(peek)
        raise LexerError('unknown symbol: %s' % self.text[:1])

    def next(self):
        return self.__parse_hex_integer(False)

    def peek(self):
        return self.__parse_hex_integer(True)

    def __iter__(self):
        return self

    def __next__(self):
        token, value = self.next()
        if token == Token.Eof:
            raise StopIteration
        return token, value


def __test():
    lex = Lexer('(1 + 2) * 3 / 4 % 5 > 3')
    for x in lex:
        print(x)

