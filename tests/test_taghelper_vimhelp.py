from taghelper import Tags, Tag
from taghelper_vimhelp import parse


def prepare(source):
    return [
        line.partition('|')[-1]
        for line in source.strip().splitlines()
    ]


def test_parse():
    buffer = prepare('''
         1|*myhelpfile.txt*  For Vim version X.Y.  Last change: 2024 Apr 26
         2|
         3|           THIS IS VERY HELPFUL
         4|
         5|Some topic                        *help-topic*
         6|
         7|Blah blah blah blah
         8|==================================================================
         9|More help text
        10|                        *another-topic*  *:lalala*
        11|:lalala         Do stuff, happily
        12|    Text text text, example:  >
        13|          :lalala *extra*
        14|
        15|          :lalala *more*
        16|
        17|  < more text, more example:  >
        18|          :lalala *extra*
        19|
        20|:blah           Do stuff, grumpily                    *last-topic*
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('myhelpfile.txt', 1, 4),
        Tag('help-topic', 5, 9),
        Tag('another-topic', 10, 19),
        Tag('last-topic', 20, 20),
    ]
