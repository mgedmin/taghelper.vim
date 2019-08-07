from taghelper import Tags, Tag
from taghelper_python import indentlevel, parse


def prepare(source):
    return [
        line.partition('|')[-1]
        for line in source.strip().splitlines()
    ]


def test_indentlevel():
    assert indentlevel('') == 0
    assert indentlevel('    ') == 4
    assert indentlevel('\t') == 8
    assert indentlevel('  \t') == 8


def test_parse_functions():
    buffer = prepare('''
        1|#!/usr/bin/python3
        2|import sys
        3|
        4|def foo(x, y):
        5|    z = x + y
        6|    return z
        7|
        8|def bar():
        9|    pass
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [Tag('foo', 4, 6), Tag('bar', 8, 9)]


def test_parse_classes():
    buffer = prepare('''
         1|#!/usr/bin/python3
         2|import sys
         3|
         4|class MyClass:
         5|    x = 42
         6|    def __init__(self):
         7|        pass
         8|
         9|    async def bar(self):
        10|        pass
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('MyClass', 4, 10),
        Tag('MyClass.__init__', 6, 7),
        Tag('MyClass.bar', 9, 10),
    ]
