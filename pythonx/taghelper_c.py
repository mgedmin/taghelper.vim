def parse(buffer, tags):
    curtag = None
    last_unindented_line = ''
    last_unindented_line_number = 1
    for n, line in enumerate(buffer, 1):
        line = line.rstrip()
        # For now we assume a particular C style:
        #   type
        #   function_name(...
        #      ...)
        #   {
        #      ...
        #   }
        # this should also work:
        #   type function_name(...
        #      ...)
        #   {
        #      ...
        #   }
        # and now I'm trying to add support for
        #   type function_name(...) {
        #      ...
        #   }
        if line[:1] == '{':
            if '(' in last_unindented_line:
                name = last_unindented_line.partition('(')[0].split()[-1]
                name = name.strip('*')
                if curtag and curtag.lastline is None:
                    curtag.lastline = last_unindented_line_number - 1
                curtag = tags.add(name, last_unindented_line_number)
                last_unindented_line = ''
        if line[:1] == '}':
            if curtag and curtag.lastline is None:
                curtag.lastline = n
        if line and (line[0].isalpha() or line[0] == '_'):
            last_unindented_line = line
            last_unindented_line_number = n
        if line.endswith(') {'):
            if '(' in last_unindented_line:
                name = last_unindented_line.partition('(')[0].split()[-1]
                name = name.strip('*')
                if curtag and curtag.lastline is None:
                    curtag.lastline = last_unindented_line_number - 1
                curtag = tags.add(name, last_unindented_line_number)
                last_unindented_line = ''
    if curtag and curtag.lastline is None:
        curtag.lastline = n
