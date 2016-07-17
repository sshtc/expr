# coding=utf-8
# author=veficos

from parse import Parser


class Environment(object):
    def __init__(self):
        self.objects = {}

    def push_object(self, name, value):
        self.objects.update({name: value})

    def pop_object(self, name):
        self.objects.pop(name)

    def get_object(self, name):
        return self.objects.get(name, None)


class Evaluator(object):
    def __init__(self, text, env):
        self.text = text
        self.env = env

    def eval(self):
        try:
            ast = Parser.parse(self.text)
            return ast.abstract_syntax_tree().eval(self.env)
        except Exception as e:
            print("eval error: ", e)

    def eval_ast(self):
        try:
            ast = Parser.parse(self.text)
            return ast.abstract_syntax_tree()
        except Exception as e:
            print("parser error: ", e)

    def eval_expression(self):
        try:
            ast = Parser.parse(self.text);
            return ast;
        except Exception as e:
            print("parser error: ", e)

while True:
    text = input('> ')

    env = Environment()
    env.push_object('ab', 1)
    env.push_object('a', [1,[11,12,13,15],3,4,5,6])
    env.push_object('math', {'add': lambda x, y: x+y})

    evaluator = Evaluator(text, env)
    print(evaluator.eval_expression())    
    print(evaluator.eval_ast())
    print(evaluator.eval())
    

