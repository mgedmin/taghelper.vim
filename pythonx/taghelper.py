"""
" HACK to make this file source'able by vim as well as importable by Python:
pyx import sys; sys.modules.pop("taghelper", None); import taghelper
finish
"""

import vim

import taghelper_c
import taghelper_diff
import taghelper_dosini
import taghelper_js
import taghelper_python


CACHE = {}

# NB: if you add a supported language, be sure to update the regex in
# autoload/taghelper.vim too!
PARSERS = {
    'c': taghelper_c.parse,
    'cpp': taghelper_c.parse,
    'python': taghelper_python.parse,
    'diff': taghelper_diff.parse,
    'javascript': taghelper_js.parse,
    'cfg': taghelper_dosini.parse,
    'dosini': taghelper_dosini.parse,
}


class Tag(object):

    def __init__(self, name, firstline, lastline=None):
        self.name = name
        self.firstline = firstline
        self.lastline = lastline
        self.level = None

    def __str__(self):
        return '%s (lines %s-%s)' % (self.name, self.firstline, self.lastline)

    def __repr__(self):
        return '<Tag: %s L%s-%s>' % (self.name, self.firstline, self.lastline)

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return NotImplemented
        # NB: ignoring level because it's an internal implementation detail
        # used by some parsers
        return (self.name, self.firstline, self.lastline) == (
            other.name, other.firstline, other.lastline)


class Tags(object):
    def __init__(self):
        self.changedtick = None
        self.tags = []
        self.syntax = ''

    def __repr__(self):
        return '<Tags: %d tags>' % len(self.tags)

    def __len__(self):
        return len(self.tags)

    def __iter__(self):
        return iter(self.tags)

    def get_syntax(self, buffer):
        syntax = buffer.vars.get('current_syntax') or ''
        if not isinstance(syntax, str):
            syntax = syntax.decode('utf-8', 'replace')
        syntax = syntax.partition('.')[0]
        return syntax

    def parse(self, buffer, changedtick):
        self.changedtick = changedtick
        self.tags = []
        self.syntax = self.get_syntax(buffer)

        parser = PARSERS.get(self.syntax)
        if parser:
            parser(buffer, self)
            self.validate()

    def add(self, name, firstline, lastline=None):
        tag = Tag(name, firstline, lastline)
        self.tags.append(tag)
        return tag

    def validate(self):
        prev = None
        for t in self.tags:
            assert t.lastline is None or t.lastline >= t.firstline
            assert prev is None or t.firstline >= prev.firstline

    def find(self, linenumber):
        best = None
        for t in self.tags:
            if linenumber >= t.firstline:
                if t.lastline is None or linenumber <= t.lastline:
                    best = t
            if t.firstline > linenumber:
                break  # haven't found anything
        return best


def gettags(bufnr=None, changedtick=None):
    if bufnr is None:
        bufnr = vim.current.buffer.number
    if changedtick is None:
        changedtick = vim.buffers[bufnr].vars['changedtick']
    cached = CACHE.get(bufnr)
    if cached is not None and cached.changedtick == changedtick:
        return cached
    tags = Tags()
    tags.parse(vim.buffers[bufnr], changedtick)
    CACHE[bufnr] = tags
    return tags


def findtag(fmt='[%s]'):
    bufnr = vim.current.buffer.number
    changedtick = vim.current.buffer.vars['changedtick']
    tags = gettags(bufnr, changedtick)
    tag = tags.find(vim.current.window.cursor[0])
    if tag:
        name = fmt % tag.name
    else:
        name = ''
    return name


def deltags(bufnr):
    CACHE.pop(bufnr, None)


def showtags(bufnr=None, changedtick=None):
    tags = gettags(bufnr, changedtick)
    print("%d tags found" % len(tags))
    for tag in tags:
        print(tag)
