import re


INDENT_COMMENT_RE = re.compile(r'(\s*)([^#]*)(.*)')
CLASS_RE = re.compile(r'class\s+([^(: \t]+).*')
DEF_RE = re.compile(r'(?:async\s*)?def\s+([^( \t]+).*')


def indentlevel(indent):
    return len(indent.expandtabs())


def parse(buffer, tags):
    stack = []
    curtag = None
    for n, line in enumerate(buffer, 1):
        match = INDENT_COMMENT_RE.match(line.rstrip())
        indent, content, comment = match.groups()

        match = CLASS_RE.match(content)
        if not match:
            match = DEF_RE.match(content)

        if match:
            name = match.group(1)
            level = indentlevel(indent)

            while stack and stack[-1].level >= level:
                oldtag = stack.pop()
                oldtag.lastline = n - 1

            if stack:
                name = '%s.%s' % (stack[-1].name, name)
            curtag = tags.add(name, n)
            curtag.level = level
            stack.append(curtag)

    while stack:
        oldtag = stack.pop()
        oldtag.lastline = n
