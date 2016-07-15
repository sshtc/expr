# coding=utf-8
# author=veficos

from analysor import Parser


class Environment(object):
    def __init__(self):
        self.objects = {}

    def add_object(self, name, value):
        self.objects.update({name: value})

    def get_object(self, name):
        return self.objects.get(name, None)


class Evaluator(object):
    def __init__(self, text, env):
        self.text = text
        self.env = env

    def eval(self):
        try:
            ast = Parser.parse(self.text)
            return ast.constant_folding().eval(self.env)
        except Exception as e:
            print("eval error: ", e)

    def ast(self):
        try:
            ast = Parser.parse(self.text)
            return ast.constant_folding()
        except Exception as e:
            print("parser error: ", e)

while True:
    text = input('> ')

    env = Environment()
    env.add_object('ab', 1)
    env.add_object('a', [1,[11,12,13,15],3,4,5,6])
    env.add_object('math', {'add': lambda x, y: x+y})

    evaluator = Evaluator(text, env)
    print(evaluator.ast())
    print(evaluator.eval())

