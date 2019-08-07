import os
import sys

import pytest


source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pythonx')
sys.path.append(source_path)


class VimStub(object):
    def __init__(self):
        self.buffers = {}
        self.current = VimCurrentStub(self)


class VimCurrentStub(object):
    def __init__(self, _vim):
        self._vim = _vim
        self.buffer = VimBufferStub()
        self.window = VimWindowStub()

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, newbuffer):
        self._buffer = newbuffer
        self._vim.buffers[newbuffer.number] = newbuffer


class VimBufferStub(object):
    def __init__(self):
        self.vars = {'changedtick': 0}
        self.number = 1

    def __iter__(self):
        return iter([])


class VimWindowStub(object):
    def __init__(self):
        self.cursor = (1, 0)
        self.vars = {}


try:
    import vim
    del vim
except ImportError:
    sys.modules['vim'] = VimStub()


@pytest.fixture(autouse=True)
def reset_cache(monkeypatch):
    import taghelper
    monkeypatch.setattr(taghelper, 'CACHE', {})


@pytest.fixture(autouse=True)
def vim(monkeypatch):
    import taghelper
    stub = VimStub()
    monkeypatch.setitem(sys.modules, 'vim', stub)
    monkeypatch.setattr(taghelper, 'vim', stub)
    return stub
