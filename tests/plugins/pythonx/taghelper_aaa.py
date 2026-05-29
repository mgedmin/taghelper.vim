TAGHELPER_PLUGIN_API_VERSION = 1
TAGHELPER_SYNTAX = ('aaa', 'aa')


def parse(buffer, tags):
    tags.add('hello_aaa', 1)
