from taghelper import Tags, Tag
from taghelper_diff import parse


def prepare(source):
    return [
        line.partition('|')[-1]
        for line in source.strip().splitlines()
    ]


def test_parse():
    buffer = prepare('''
         1|--- a/foo/bar.py
         2|+++ b/foo/bar.py
         3|@@ -1,10 +1,16 @@
         4| import re
         5|+import logging
         6| import urllib
         7|+import importlib
         8|
         9|--- /dev/null
        10|+++ b/new.txt
        11|@@ -0,0 +1,2 @@
        12|+hello
        13|+world
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('foo/bar.py', 1, 8),
        Tag('new.txt', 9, 13),
    ]


def test_parse_git_diff():
    buffer = prepare('''
         1|diff --git a/foo/bar.py b/foo/bar.py
         2|index 54737257c..78871090f 100644
         3|--- a/foo/bar.py
         4|+++ b/foo/bar.py
         5|@@ -1,10 +1,16 @@
         6| import re
         7|+import logging
         8| import urllib
         9|+import importlib
        10|
        11|diff --git a/new.txt b/new.txt
        12|new file mode 100644
        13|index 000000000..78871090f
        14|--- /dev/null
        15|+++ b/new.txt
        16|@@ -0,0 +1,2 @@
        17|+hello
        18|+world
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('foo/bar.py', 1, 10),
        Tag('new.txt', 11, 18),
    ]
