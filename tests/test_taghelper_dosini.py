from taghelper import Tags, Tag
from taghelper_dosini import parse


def prepare(source):
    return [
        line.partition('|')[-1]
        for line in source.strip().splitlines()
    ]


def test_parse():
    buffer = prepare('''
         1|[settings]
         2|x = 1
         3|y = 2
         4|
         5|
         6|[more-settings] ; comment
         7|z = 3
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('[settings]', 1, 5),
        Tag('[more-settings]', 6, 7),
    ]
