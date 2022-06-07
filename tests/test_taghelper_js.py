from taghelper import Tags, Tag
from taghelper_js import parse


def prepare(source):
    return [
        line.partition('|')[-1]
        for line in source.strip().splitlines()
    ]


def test_parse_functions():
    buffer = prepare('''
         1|import React from 'react';
         2|
         3|class ColorComponent extends React.Component {
         4|  static get contextTypes() {
         5|    return {
         6|      intl: intlShape.isRequired,
         7|    };
         8|  }
         9|
        10|  render() {
        11|    const { formatMessage } = this.context.intl;
        12|    return (
        13|      <div>
        14|        blah blah who cares
        15|      </div>
        16|    );
        17|  }
        18|
        19|}
    ''')
    tags = Tags()
    parse(buffer, tags)
    assert tags.tags == [
        Tag('ColorComponent', 3, 19),
        Tag('ColorComponent.contextTypes', 4, 8),
        Tag('ColorComponent.render', 10, 17),
    ]
