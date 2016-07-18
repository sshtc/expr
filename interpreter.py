# coding=utf-8
# author=veficos

from expr import Environment, Executor

while True:
    text = input('> ')
    if not text:
        continue

    env = Environment()
    env.push_object('number', 1)
    env.push_object('list', [1, [11, {'add': lambda x, y: x+y}, 13, 15], 3, 4, 5, 6])
    env.push_object('math', {'add': lambda x, y: x+y})
    env.push_object('env', {'print': lambda: print(env)})

    try:
        evaluator = Executor(text, env)
        print(evaluator.exec())
        print(evaluator.ast())
    except Exception as e:
        print(e)