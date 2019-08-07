from taghelper import Tag, Tags, gettags, findtag, deltags, showtags


class BufferStub:
    def __init__(self, lines=(), vars=(), number=1):
        self.number = number
        self.vars = dict(changedtick=42)
        self.vars.update(vars)
        self.lines = lines

    def __iter__(self):
        return iter(self.lines)


def test_Tag_str():
    tag = Tag('foo', 1, 2)
    assert str(tag) == 'foo (lines 1-2)'


def test_Tag_repr():
    tag = Tag('foo', 1, 2)
    assert repr(tag) == '<Tag: foo L1-2>'


def test_Tag_equality():
    tag1 = Tag('foo', 1, 2)
    tag2 = Tag('foo', 1, 2)
    tag3 = Tag('foo', 1, 3)
    assert tag1 == tag2
    assert tag1 != tag3
    assert tag1 != 42


def test_Tags_repr():
    tags = Tags()
    assert repr(tags) == '<Tags: 0 tags>'
    tags.add('foo', 1, 2)
    assert repr(tags) == '<Tags: 1 tags>'


def test_Tags_len():
    tags = Tags()
    assert len(tags) == 0
    tags.add('foo', 1, 2)
    assert len(tags) == 1


def test_Tags_iter():
    tags = Tags()
    assert list(tags) == []
    tags.add('foo', 1, 2)
    assert list(tags) == [Tag('foo', 1, 2)]


def test_Tags_get_syntax():
    tags = Tags()
    assert tags.get_syntax(BufferStub()) == ''
    assert tags.get_syntax(BufferStub(vars={'current_syntax': b''})) == ''
    assert tags.get_syntax(BufferStub(vars={'current_syntax': b'cpp'})) == 'cpp'
    assert tags.get_syntax(BufferStub(vars={'current_syntax': b'c.x'})) == 'c'


def test_Tags_parse_no_syntax():
    tags = Tags()
    tags.parse(BufferStub(), 42)
    assert tags.changedtick == 42
    assert tags.tags == []


def test_Tags_parse_python():
    tags = Tags()
    tags.parse(BufferStub([
        'def foo():',
        '    pass',
    ], vars={'current_syntax': b'python'}), 42)
    assert tags.changedtick == 42
    assert tags.tags == [Tag('foo', 1, 2)]


def test_Tags_add():
    tags = Tags()
    tag = tags.add('foo', 1, 2)
    assert tag == Tag('foo', 1, 2)
    assert tags.tags == [tag]


def test_Tags_find():
    tags = Tags()
    foo = tags.add('foo', 3, 7)
    bar = tags.add('bar', 10)
    assert tags.find(1) is None
    assert tags.find(2) is None
    assert tags.find(3) is foo
    assert tags.find(4) is foo
    assert tags.find(7) is foo
    assert tags.find(8) is None
    assert tags.find(9) is None
    assert tags.find(10) is bar
    assert tags.find(11) is bar


def test_Tags_find_overlapping():
    tags = Tags()
    foo = tags.add('Foo', 3, 20)
    foo_bar = tags.add('Foo.bar', 10, 17)
    assert tags.find(3) is foo
    assert tags.find(10) is foo_bar
    assert tags.find(17) is foo_bar
    assert tags.find(18) is foo


def test_getttags(vim):
    vim.buffers[3] = BufferStub(number=3)
    vim.buffers[4] = BufferStub(number=4)

    tags1 = gettags(3, 42)
    tags2 = gettags(3, 42)
    assert tags1 is tags2

    tags3 = gettags(4, 42)
    assert tags3 is not tags1

    tags4 = gettags(3, 43)
    assert tags4 is not tags1

    vim.current.buffer = vim.buffers[3]
    vim.current.buffer.vars['changedtick'] = 43
    assert gettags() is tags4


def test_findtag(vim):
    vim.current.buffer = BufferStub([
        '# comment',
        'def foo():',
        '    pass',
    ], vars={'current_syntax': b'python'})
    assert findtag() == ''
    vim.current.window.cursor = (2, 0)
    assert findtag() == '[foo]'


def test_deltags(vim):
    vim.buffers[3] = BufferStub(number=3)
    tags1 = gettags(3, 42)
    deltags(3)
    tags2 = gettags(3, 42)
    assert tags1 is not tags2


def test_showtags_none(vim, capsys):
    vim.buffers[3] = BufferStub(number=3)
    showtags(3, 42)
    assert capsys.readouterr().out == '0 tags found\n'


def test_showtags_some(vim, capsys):
    vim.current.buffer = BufferStub([
        'def foo():',
        '    pass',
    ], vars={'current_syntax': b'python'})
    showtags(1, 42)
    assert capsys.readouterr().out == '1 tags found\nfoo (lines 1-2)\n'
