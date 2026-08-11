# https://docs.ruby-lang.org/en/4.0/syntax/methods_rdoc.html
# https://docs.ruby-lang.org/en/4.0/syntax/modules_and_classes_rdoc.html

import re


ident_start = r'[a-zA-Z\x80-\U0010FFFF]'
ident_continue = r'[a-zA-Z0-9_\x80-\U0010FFFF]'
ident = f'{ident_start}{ident_continue}*'
operator = r'(?:[*/%&|^<>]|\*\*|>>|<<|[=!<>]=|===|[=!]~|<=>|\[]=?|[-+~!]@?)'

spaces = r'\s+'
optspaces = r'\s*'

capture_indent = r'(?P<indent>\s*)'
capture_name = f'(?:{ident}[.])?(?P<name>(?:{ident}[!?=]?|{operator}))'
capture_module_name = f'(?P<name>(?:{ident}::)*{ident})'
capture_class_name = f'(?:<<{optspaces})?(?P<name>(?:{ident}::)*{ident})'

# technically I should be matching balanced parentheses here
# to allow def my_method((a, b)) = ... but not get confused by
# def my_method(a = ...)
opt_parens = r'(?:\s*[(][^)]*[)])?'

INDENT_RE = re.compile(r'\s*')

DEF_RE = re.compile(f'{capture_indent}def{spaces}{capture_name}')
END_RE = re.compile(f'{capture_indent}end\\b')
INLINE_DEF_RE = re.compile(
    f'{capture_indent}def{spaces}{capture_name}{opt_parens}{spaces}='
)

MODULE_RE = re.compile(f'{capture_indent}module{spaces}{capture_module_name}')
CLASS_RE = re.compile(f'{capture_indent}class{spaces}{capture_class_name}')


def indentlevel(indent):
    return len(indent.expandtabs())


class Parser:
    def __init__(self, tags):
        self.tags = tags
        self.stack = []

    def get_scope(self, kind):
        if not self.stack:
            return ''
        curtag = self.stack[-1]
        sep = '.' if kind == 'method' else '::'
        return f'{curtag.name}{sep}'

    def add(self, match, kind, lineno, lastline=None):
        level = indentlevel(match['indent'])
        self.close_up_to(level, lineno - 1)
        curtag = self.tags.add(
            self.get_scope(kind) + match['name'], lineno, lastline=lastline
        )
        curtag.kind = kind
        curtag.level = level
        if not lastline:
            self.stack.append(curtag)

    def close_up_to(self, level, lineno):
        while self.stack and self.stack[-1].level >= level:
            self.stack.pop().lastline = lineno

    def parse(self, buffer):
        for n, line in enumerate(buffer, 1):
            if m := INLINE_DEF_RE.match(line):
                self.add(m, 'method', n, lastline=n)
            elif m := DEF_RE.match(line):
                self.add(m, 'method', n)
            elif m := MODULE_RE.match(line):
                self.add(m, 'module', n)
            elif m := CLASS_RE.match(line):
                self.add(m, 'class', n)
            elif m := END_RE.match(line):
                level = indentlevel(m['indent'])
                self.close_up_to(level, n)


def parse(buffer, tags):
    Parser(tags).parse(buffer)
