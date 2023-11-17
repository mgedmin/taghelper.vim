
def parse(buffer, tags):
    curtag = None
    for n, line in enumerate(buffer, 1):
        if line.startswith('[') and ']' in line:
            section = line[:line.index(']') + 1]
            if curtag:
                curtag.lastline = n - 1
            curtag = tags.add(section, n)
    if curtag:
        curtag.lastline = n
