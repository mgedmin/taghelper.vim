from taghelper import Tag, Tags
from taghelper_ruby import indentlevel, parse


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


def test_parse_methods():
    buffer = prepare('''
         1|#!/usr/bin/ruby
         2|
         3|def one_plus_one
         4|  1 + 1
         5|end
         6|
         7|def one_plus_two = 1 + 2
         8|
         9|def こんにちは
        10|  puts "means hello in Japanese"
        11|end
        12|
        13|def add_values(a = 1, b = 2, c)
        14|  a + b + c
        15|end
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('one_plus_one', 3, 5),
        Tag('one_plus_two', 7, 7),
        Tag('こんにちは', 9, 11),
        Tag('add_values', 13, 15),
    ]


def test_parse_class_and_methods():
    buffer = prepare('''
         1|#!/usr/bin/ruby
         2|
         3|class C
         4|  def attr
         5|    @attr
         6|  end
         7|
         8|  def attr=(val)
         9|    @attr = val
        10|  end
        11|end
        12|
        13|class D
        14|  def -@
        15|    puts "you inverted this objet"
        16|  end
        17|end
        18|
        19|class E
        20|  def [](a, b)
        21|    puts a + b
        22|  end
        23|
        24|  def []=(a, b, c)
        25|    puts a * b + c
        26|  end
        27|end
        28|
        29|class F
        30|  def self.my_method
        31|    # ...
        32|  end
        33|end
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('C', 3, 11),
        Tag('C.attr', 4, 6),
        Tag('C.attr=', 8, 10),
        Tag('D', 13, 17),
        Tag('D.-@', 14, 16),
        Tag('E', 19, 27),
        Tag('E.[]', 20, 22),
        Tag('E.[]=', 24, 26),
        Tag('F', 29, 33),
        Tag('F.my_method', 30, 32),
    ]


def test_parse_class_in_module():
    buffer = prepare('''
         1|require '...'
         2|
         3|class A::B::C::D < E::F
         4|  ...
         5|  def self.foo(bar)
         6|    ...
         7|  end
         8|
         9|  def bar(baz)
        10|    ...
        11|  end
        12|end
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('A::B::C::D', 3, 12),
        Tag('A::B::C::D.foo', 5, 7),
        Tag('A::B::C::D.bar', 9, 11),
    ]


def test_parse_modules():
    buffer = prepare('''
         1|#!/usr/bin/ruby
         2|
         3|module MyModule
         4|  def my_method
         5|  end
         6|end
         7|
         8|module Outer
         9|  module Inner
        10|  end
        11|end
        12|
        13|module Outer::Inner::GrandChild
        14|end
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('MyModule', 3, 6),
        Tag('MyModule.my_method', 4, 5),
        Tag('Outer', 8, 11),
        Tag('Outer::Inner', 9, 10),
        Tag('Outer::Inner::GrandChild', 13, 14),
    ]


def test_parse_sameline():
    buffer = prepare('''
         1|module A; module B; module C; end; end; end;
         2|
         3|class A::B::C::D
         4|  def initialize(...)
         5|  end
         6|end
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('A', 1, 2),  # technically this should end on line 1
        # technically there should be tags for A::B and A::B::C on line 1
        Tag('A::B::C::D', 3, 6),
        Tag('A::B::C::D.initialize', 4, 5),
    ]
