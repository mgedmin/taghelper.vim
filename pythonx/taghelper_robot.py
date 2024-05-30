# Robot Framework test files, see https://robotframework.org
def parse(buffer, tags):
    sectiontag = None
    curtag = None
    cursection = ''
    for n, line in enumerate(buffer, 1):
        if line.startswith('*'):
            section = line.rstrip()
            if curtag:
                curtag.lastline = n - 1
            if sectiontag:
                sectiontag.lastline = n - 1
            sectiontag = tags.add(section, n)
            cursection = section.strip('* ').lower()
            curtag = None
        if cursection in ('test cases', 'tasks', 'keywords'):
            if line and line[:1].isalpha() and '  ' not in line:
                name = line.strip()
                if curtag:
                    curtag.lastline = n - 1
                curtag = tags.add(name, n)
    if curtag:
        curtag.lastline = n
    if sectiontag:
        sectiontag.lastline = n
