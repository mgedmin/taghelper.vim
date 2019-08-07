
def clean_filename(filename):
    if filename.startswith(('a/', 'b/')):
        filename = filename[2:]
    return filename


def parse(buffer, tags):
    curtag = None
    diff_start = False
    for n, line in enumerate(buffer, 1):
        if line.startswith('diff'):
            # diff [--git] file1 file2
            parts = line.split()
            if len(parts) >= 3:
                filename = clean_filename(parts[-2])
                if curtag:
                    curtag.lastline = n - 1
                curtag = tags.add(filename, n)
                diff_start = True
        elif line.startswith('--- ') and not diff_start:
            filename = clean_filename(line[4:])
            if curtag and curtag.lastline is None:
                curtag.lastline = n - 1
            curtag = tags.add(filename, n)
        elif line.startswith('+++ ') and curtag and curtag.name == '/dev/null':
            curtag.name = clean_filename(line[4:])
        elif line.startswith(' '):
            diff_start = False
    if curtag:
        curtag.lastline = n
