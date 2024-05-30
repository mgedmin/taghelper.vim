from taghelper import Tags, Tag
from taghelper_robot import parse


def prepare(source):
    return [
        line.partition('|')[-1]
        for line in source.strip().splitlines()
    ]


def test_parse():
    buffer = prepare('''
         1|*** Settings ***
         2|Documentation     Example using the space separated format.
         3|Library           OperatingSystem
         4|
         5|*** Variables ***
         6|${MESSAGE}        Hello, world!
         7|
         8|*** Test Cases ***
         9|My Test
        10|    [Documentation]    Example test.
        11|    Log    ${MESSAGE}
        12|    My Keyword    ${CURDIR}
        13|
        14|Another Test
        15|    Should Be Equal    ${MESSAGE}    Hello, world!
        16|
        17|*** Keywords ***
        18|My Keyword
        19|    [Arguments]    ${path}
        20|    Directory Should Exist    ${path}
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('*** Settings ***', 1, 4),
        Tag('*** Variables ***', 5, 7),
        Tag('*** Test Cases ***', 8, 16),
        Tag('My Test', 9, 13),
        Tag('Another Test', 14, 16),
        Tag('*** Keywords ***', 17, 20),
        Tag('My Keyword', 18, 20),
    ]
