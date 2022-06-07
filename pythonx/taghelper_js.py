import re


CLASS_RE = re.compile(r'(\s*)(?:export\s+)?class\s+([^(: \t]+).*')

FUNC_RE = re.compile(
    r'(\s*)(?:static\s+)?(?:get\s+)?([^(: \t]+)[(].*[)]\s*{$')

CLOSING_RE = re.compile(r'(\s*)}$')


def indentlevel(indent):
    return len(indent.expandtabs())


def parse(buffer, tags):
    curtag = None
    stack = []

    for n, line in enumerate(buffer, 1):
        match = CLASS_RE.match(line)
        if match:
            indent, name = match.groups()
            curtag = tags.add(name, n)
            curtag.level = indentlevel(indent)
            stack.append(curtag)

        match = FUNC_RE.match(line)
        if match:
            indent, name = match.groups()
            if stack:
                name = '%s.%s' % (stack[-1].name, name)
            curtag = tags.add(name, n)
            curtag.level = indentlevel(indent)
            stack.append(curtag)

        match = CLOSING_RE.match(line)
        if match:
            indent = match.group(1)
            level = indentlevel(indent)
            while stack and stack[-1].level >= level:
                oldtag = stack.pop()
                oldtag.lastline = n

    while stack:
        oldtag = stack.pop()
        oldtag.lastline = n
