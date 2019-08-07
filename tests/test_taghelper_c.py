from taghelper import Tags, Tag
from taghelper_c import parse


def prepare(source):
    return [
        line.partition('|')[-1]
        for line in source.strip().splitlines()
    ]


def test_parse():
    buffer = prepare('''
         1|int foo()
         2|{
         3|    return 42;
         4|}
         5|
         6|char *hello(void)
         7|{
         8|    return "world";
         9|}
        10|
        11|int
        12|main()
        13|{
        14|    foo();
        15|    return 0;
        16|}
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('foo', 1, 4),
        Tag('hello', 6, 9),
        Tag('main', 12, 16),
    ]


def test_parse_cpp():
    buffer = prepare('''
         1|class Foo {
         2|public:
         3|    Foo()
         4|    ~Foo()
         5|private:
         6|    int x;
         7|}
         8|
         9|Foo::Foo() {
        10|    x = 42;
        11|}
        12|
        13|Foo::~Foo() {
        14|}
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('Foo::Foo', 9, 11),
        Tag('Foo::~Foo', 13, 14),
    ]


def test_no_overlaps_if_parser_gets_confused():
    buffer = prepare('''
         1|#if FOO
         2|int foo() {
         3|#else
         4|int foo(int x) {
         5|#endif
         6|    return 42;
         7| }
         8|
         9|int bar(int x)
        10|{
        11|    return 42;
        12| }
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('foo', 2, 3),
        Tag('foo', 4, 8),  # or should I insist on 4, 7?
        Tag('bar', 9, 12),
    ]
