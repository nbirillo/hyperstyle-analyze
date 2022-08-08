import textwrap
from typing import Dict, Optional

import pytest

from analysis.src.python.data_analysis.preprocessing.preprocess_hidden_templates import Template, TemplateBlock


HEADER = 'import numpy as np'

CODE_PLACEHOLDER = '// Write your code here'

CODE = textwrap.dedent(
    """
    def get_hello_world() -> str:
        return "Hello, world!"
    """,
).strip()

FOOTER = textwrap.dedent(
    """
    def main():
        print(get_hello_world())
        
    if __name__ == '__main__':
        main()
    """
).strip()

TEMPLATE = textwrap.dedent(
    """
    ::python3
    ::header
    import numpy as np

    ::code
    // Write your code here

    ::footer
    def main():
        print(get_hello_world())
        
    if __name__ == '__main__':
        main()
    """,
).strip()


BAD_TEMPLATE = textwrap.dedent(
    """
    
    
    ::python3
    ::header
    import numpy as np






    ::code
    // Write your code here
    ::footer
    def main():
        print(get_hello_world())

    if __name__ == '__main__':
        main()







    """,
).strip()


COMPILE_TEMPLATE_TEST_DATA = [
    (None, None, False, ""),
    (None, None, True, ""),
    (
        None,
        {TemplateBlock.CODE: CODE},
        False,
        CODE,
    ),
    (
        None,
        {TemplateBlock.CODE: CODE},
        True,
        CODE + '\n',
    ),
    (
        None,
        {TemplateBlock.HEADER: HEADER, TemplateBlock.CODE: CODE, TemplateBlock.FOOTER: FOOTER},
        False,
        f'{HEADER}\n{CODE}\n{FOOTER}',
    ),
    (
        None,
        {TemplateBlock.HEADER: HEADER, TemplateBlock.CODE: CODE, TemplateBlock.FOOTER: FOOTER},
        True,
        f'{HEADER}\n\n{CODE}\n\n{FOOTER}\n',
    ),
    (
        TEMPLATE,
        None,
        False,
        f'{HEADER}\n{CODE_PLACEHOLDER}\n{FOOTER}',
    ),
    (
        TEMPLATE,
        None,
        True,
        f'{HEADER}\n\n{CODE_PLACEHOLDER}\n\n{FOOTER}\n',
    ),
    (
        TEMPLATE,
        {TemplateBlock.CODE: CODE},
        False,
        f'{HEADER}\n{CODE}\n{FOOTER}',
    ),
    (
        TEMPLATE,
        {TemplateBlock.CODE: CODE},
        True,
        f'{HEADER}\n\n{CODE}\n\n{FOOTER}\n',
    ),
    (
        BAD_TEMPLATE,
        None,
        False,
        f'{HEADER}\n{CODE_PLACEHOLDER}\n{FOOTER}',
    ),
    (
        BAD_TEMPLATE,
        None,
        True,
        f'{HEADER}\n\n{CODE_PLACEHOLDER}\n\n{FOOTER}\n',
    ),
    (
        BAD_TEMPLATE,
        {TemplateBlock.CODE: CODE},
        False,
        f'{HEADER}\n{CODE}\n{FOOTER}',
    ),
    (
        BAD_TEMPLATE,
        {TemplateBlock.CODE: CODE},
        True,
        f'{HEADER}\n\n{CODE}\n\n{FOOTER}\n',
    ),
]


@pytest.mark.parametrize(
    ('template_content', 'new_block_content', 'separate_blocks', 'expected_code'),
    COMPILE_TEMPLATE_TEST_DATA,
)
def test_compile_template(
    template_content: Optional[str],
    new_block_content: Optional[Dict[TemplateBlock, str]],
    separate_blocks: bool,
    expected_code: Optional[str],
):
    code = Template(template_content).compile_template(new_block_content, separate_blocks)
    assert code == expected_code
