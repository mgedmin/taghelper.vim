import re

INDENT_COMMENT_RE = re.compile(r'(\s*)([^#]*)(.*)')
CLASS_RE = re.compile(r'class\s+([^(: \t]+).*')
DEF_RE = re.compile(r'(?:async\s*)?def\s+([^( \t]+).*')
DECORATOR_RE = re.compile(r'@')
ASSIGNMENT_RE = re.compile(
    r'^([a-zA-Z_][a-zA-Z_0-9]*)\s*(?::.*)?=\s([\[({]|[(]?[fr]?(?:"""|\'\'\'))$'
)


CLOSING = {
    '[': ']',
    '{': '}',
    '(': ')',
    '"""': '"""',
    "'''": "'''",
    'f"""': '"""',
    "f'''": "'''",
    'r"""': '"""',
    "r'''": "'''",
    '("""': '""")',
    "('''": "''')",
    '(f"""': '""")',
    "(f'''": "''')",
    '(r"""': '""")',
    "(r'''": "''')",
}


def indentlevel(indent):
    return len(indent.expandtabs())


def parse(buffer, tags):
    stack = []
    curtag = None
    closing = None
    closes_with_indent = False
    first_decorator_line = None
    for n, line in enumerate(buffer, 1):
        match = INDENT_COMMENT_RE.match(line.rstrip())
        indent, content, comment = match.groups()

        match = DECORATOR_RE.match(content)
        if match and first_decorator_line is None:
            first_decorator_line = n
            continue

        match = CLASS_RE.match(content)
        if not match:
            match = DEF_RE.match(content)

        if match:
            closing = None
            closes_with_indent = True

        if not match and not indent:
            match = ASSIGNMENT_RE.match(content)
            if match:
                closing = CLOSING[match.group(2)]
                closes_with_indent = False

        if match:
            name = match.group(1)
            level = indentlevel(indent)
            start = n
            if first_decorator_line is not None:
                start = first_decorator_line

            while stack and stack[-1].level >= level:
                oldtag = stack.pop()
                oldtag.lastline = start - 1

            if stack:
                name = '%s.%s' % (stack[-1].name, name)
            curtag = tags.add(name, start)
            curtag.level = level
            stack.append(curtag)

            first_decorator_line = None
        elif content == closing:
            if not closes_with_indent:
                oldtag = stack.pop()
                oldtag.lastline = n
            closing = None
        elif (closes_with_indent and content and first_decorator_line is None
              and not content.startswith(')')):
            level = indentlevel(indent)
            while stack and stack[-1].level >= level:
                oldtag = stack.pop()
                oldtag.lastline = n - 1

    while stack:
        oldtag = stack.pop()
        oldtag.lastline = n
