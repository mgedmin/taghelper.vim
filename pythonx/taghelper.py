"""
" HACK to make this file source'able by vim as well as importable by Python:
pyx import sys; sys.modules.pop("taghelper", None); import taghelper
finish
"""

import importlib
import glob
import os

import vim

import taghelper_c
import taghelper_diff
import taghelper_dosini
import taghelper_js
import taghelper_python
import taghelper_robot
import taghelper_vimhelp


CACHE = {}

PARSERS = {
    'c': taghelper_c.parse,
    'cpp': taghelper_c.parse,
    'python': taghelper_python.parse,
    'diff': taghelper_diff.parse,
    'javascript': taghelper_js.parse,
    'cfg': taghelper_dosini.parse,
    'dosini': taghelper_dosini.parse,
    'robot': taghelper_robot.parse,
    'help': taghelper_vimhelp.parse,
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

    def close(self, lastline):
        self.lastline = lastline


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
            verbose_print(f'parsing buffer {buffer.number} for {self.syntax}')
            parser(buffer, self)
            self.validate()
        else:
            verbose_print(f'no parser for {self.syntax}')

    def add(self, name, firstline, lastline=None, autoclose=False):
        if autoclose:
            self.autoclose(firstline - 1)
        tag = Tag(name, firstline, lastline)
        self.tags.append(tag)
        return tag

    def autoclose(self, lastline, all=False):
        for tag in reversed(self.tags):
            if tag.lastline is None:
                tag.lastline = lastline
            elif not all:
                break

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


def verbose_print(msg):
    verbose = vim.bindeval('&verbose')
    if verbose >= 1:
        print(msg)


def load_plugins():
    vimruntime = vim.bindeval('&rtp')
    for path in vimruntime.split(b','):
        # here we assume python2 is dead dead dead
        for subpath in b'pythonx', b'python3':
            for fn in glob.glob(os.path.join(path, subpath, b'taghelper_*.py')):
                name = os.path.basename(fn).removesuffix(b'.py').decode('UTF-8')
                try:
                    mod = importlib.import_module(name)
                except ImportError as e:
                    verbose_print(f'skipping {name}: {e}')
                    continue
                else:
                    if not hasattr(mod, 'TAGHELPER_PLUGIN_API_VERSION'):
                        verbose_print(f'skipping {name}: TAGHELPER_PLUGIN_API_VERSION not defined')
                        continue
                    apiver = mod.TAGHELPER_PLUGIN_API_VERSION
                    if apiver != 1:
                        verbose_print(f'skipping {name}: TAGHELPER_PLUGIN_API_VERSION is {apiver}, not 1')
                        continue
                    PARSERS[mod.TAGHELPER_SYNTAX] = mod.parse
                    verbose_print(f'loaded {name}')
    vim.vars['taghelper_supported_syntax'] = supported_syntax()


def gettags(bufnr=None, changedtick=None):
    if bufnr is None:
        bufnr = vim.current.buffer.number
    if changedtick is None:
        changedtick = vim.buffers[bufnr].vars['changedtick']
    cached = CACHE.get(bufnr)
    if cached is not None and cached.changedtick == changedtick:
        verbose_print(f'using cached tags for buffer {bufnr}')
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


def clear_caches():
    CACHE.clear()


def showtags(bufnr=None, changedtick=None):
    tags = gettags(bufnr, changedtick)
    print("%d tags found" % len(tags))
    for tag in tags:
        print(tag)


def supported_syntax():
    return r'^\({}\)\(\.\|$\)'.format(r'\|'.join(PARSERS))
