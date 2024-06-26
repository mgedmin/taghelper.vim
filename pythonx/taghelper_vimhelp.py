# Vim help files
import re

TAG_RE = re.compile(r'[*]([#-)!+-~]+)[*]')


def parse(buffer, tags):
    curtag = None
    in_example = False
    for n, line in enumerate(buffer, 1):
        if line and not line[:1].isspace() or line.lstrip().startswith('<'):
            in_example = False
        m = TAG_RE.search(line)
        if m and not in_example:
            name = m.group(1)
            if curtag:
                curtag.lastline = n - 1
            curtag = tags.add(name, n)
        if line.endswith('>'):
            in_example = True
    if curtag:
        curtag.lastline = n
