# coding=utf-8
# author=veficos

from .elexer import *
from .east import *


class GrammarError(Exception):
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer

    def __parse_if_expression(self):
        if_expr = self.__parse_or_expression()
        tok, _ = self.lexer.peek()

        while tok == Token.If:
            self.lexer.next()
            condition = self.parse()

            tok, _ = self.lexer.next()
            if tok != Token.Else:
                raise GrammarError('excepted "else"')

            else_expr = self.parse()
            if_expr = If(if_expr, condition, else_expr)

        return if_expr

    def __parse_or_expression(self):
        lexpr = self.__parse_and_expression()
        tok, _ = self.lexer.peek()
        while tok == Token.Or:
            self.lexer.next()
            rexpr = self.__parse_and_expression()
            lexpr = LogicalOr(lexpr, rexpr)
            tok, _ = self.lexer.peek()
        return lexpr

    def __parse_and_expression(self):
        lexpr = self.__parse_equality_expression()
        tok, _ = self.lexer.peek()
        while tok == Token.And:
            self.lexer.next()
            rexpr = self.__parse_equality_expression()
            lexpr = LogicalAnd(lexpr, rexpr)
            tok, _ = self.lexer.peek()
        return lexpr

    def __parse_equality_expression(self):
        to_ast = {Token.Eq: Equal, Token.Neq: UnEqual}
        toks = to_ast.keys()

        lexpr = self.__parse_relational_expression()
        tok, _ = self.lexer.peek()
        while any(map(lambda x: x == tok, toks)):
            self.lexer.next()
            rexpr = self.__parse_relational_expression()
            lexpr = to_ast[tok](lexpr, rexpr)
            tok, _ = self.lexer.peek()
        return lexpr

    def __parse_relational_expression(self):
        to_ast = {Token.Lt: LessThan, Token.Leq: LessOrEqual, Token.Gt: GreaterThan, Token.Geq: GreaterOrEqual}
        toks = to_ast.keys()

        lexpr = self.__parse_additive_expression()
        tok, _ = self.lexer.peek()
        while any(map(lambda x: x == tok, toks)):
            self.lexer.next()
            rexpr = self.__parse_additive_expression()
            lexpr = to_ast[tok](lexpr, rexpr)
            tok, _ = self.lexer.peek()
        return lexpr

    def __parse_additive_expression(self):
        to_ast = {Token.Add: Add, Token.Sub: Subtract}
        toks = to_ast.keys()

        lexpr = self.__parse_multiplicative_expression()
        tok, _ = self.lexer.peek()
        while any(map(lambda x: x == tok, toks)):
            self.lexer.next()
            rexpr = self.__parse_multiplicative_expression()
            lexpr = to_ast[tok](lexpr, rexpr)
            tok, _ = self.lexer.peek()
        return lexpr

    def __parse_multiplicative_expression(self):
        to_ast = {Token.Mul: Multiply, Token.Div: Divide, Token.Mod: IntegerDivide}
        toks = to_ast.keys()

        lexpr = self.__parse_unary_expression()
        tok, _ = self.lexer.peek()
        while any(map(lambda x: x == tok, toks)):
            self.lexer.next()
            rexpr = self.__parse_unary_expression()
            lexpr = to_ast[tok](lexpr, rexpr)
            tok, _ = self.lexer.peek()
        return lexpr

    def __parse_unary_expression(self):
        tok, _ = self.lexer.peek()
        if tok == Token.Add:
            self.lexer.next()
            ast = self.__parse_postfix_expression()
        elif tok == Token.Sub:
            self.lexer.next()
            ast = Negative(self.__parse_postfix_expression())
        elif tok == Token.Not:
            self.lexer.next()
            ast = Not(self.__parse_postfix_expression())
        else:
            ast = self.__parse_postfix_expression()
        return ast

    def __parse_postfix_expression(self):
        ast = self.__parse_primary_expression()
        tok, _ = self.lexer.peek()

        while any(map(lambda x: x == tok, [Token.LeftBracket, Token.LeftParentheses, Token.Dot])):
            if tok == Token.LeftParentheses:
                args = []
                self.lexer.next()
                tok, _ = self.lexer.peek()

                while tok != Token.RightParentheses:
                    args.append(self.parse())
                    tok, _ = self.lexer.peek()
                    if tok != Token.Comma:
                        break
                    tok, _ = self.lexer.next()

                if tok != Token.RightParentheses:
                    raise GrammarError('expected ")"')
                self.lexer.next()

                ast = FunctionCall(ast, args)

            elif tok == Token.LeftBracket:
                self.lexer.next()
                ast = Subscript(ast, self.parse())
                if self.lexer.peek()[0] != Token.RightBracket:
                    raise GrammarError('expected "]"')
                self.lexer.next()

            elif tok == Token.Dot:
                self.lexer.next()
                tok, value = self.lexer.next()
                if tok != Token.Identifier:
                    raise GrammarError('expected identifier')
                ast = Member(ast, value)

            tok, _ = self.lexer.peek()

        return ast

    def __parse_primary_expression(self):
        tok, value = self.lexer.peek()

        if tok == Token.IntegerConstant:
            ast = IntegerConstant(value)
        elif tok == Token.DecimalConstant:
            ast = DecimalConstant(value)
        elif tok == Token.StringConstant:
            ast = StringConstant(value)
        elif tok == Token.TrueConstant:
            ast = BoolConstant(value)
        elif tok == Token.FalseConstant:
            ast = BoolConstant(value)
        elif tok == Token.NilConstant:
            ast = NilConstant(value)
        elif tok == Token.Identifier:
            ast = Symbol(value)
        elif tok == Token.LeftParentheses:
            self.lexer.next()
            ast = self.parse()
            if self.lexer.peek()[0] != Token.RightParentheses:
                raise GrammarError('expected ")"')
        else:
            raise GrammarError(('undefined grammar: %s' % str(value))
                               if tok != Token.Eof else 'expected a expression grammar')

        self.lexer.next()
        return ast

    def parse(self):
        return self.__parse_if_expression()


def __test():
    while True:
        text = input()
        parser = Parser(Lexer(text))
        print(repr(parser.parse().eval(None)))