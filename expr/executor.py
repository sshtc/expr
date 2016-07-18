# coding=utf-8
# author=veficos

from .elexer import Lexer
from .eparser import Parser


class Environment(object):
    def __init__(self):
        self.objects = {}

    def push_object(self, name, value):
        self.objects.update({name: value})

    def pop_object(self, name):
        self.objects.pop(name)

    def get_object(self, name):
        return self.objects.get(name, None)

    def __repr__(self):
        return str(self.objects)


class Executor(object):
    def __init__(self, text, env):
        self.text = text
        self.env = env

    def exec(self):
        try:
            ast = Parser(Lexer(self.text)).parse()
            return ast.eval(self.env)
        except Exception as e:
            print("eval error: ", e)

    def ast(self):
        try:
            ast = Parser(Lexer(self.text)).parse()
            return ast
        except Exception as e:
            print("parser error: ", e)
