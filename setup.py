import os
from pathlib import Path
from typing import List

from setuptools import find_packages, setup

current_dir = Path(__file__).parent.absolute()


def get_long_description() -> str:
    with open(current_dir / 'README.md', encoding='utf-8') as f:
        return f.read()


def get_version() -> str:
    with open(current_dir / 'VERSION.md') as version_file:
        return version_file.read().replace('\n', '')


def get_requires() -> List[str]:
    with open(current_dir / 'requirements.txt') as requirements_file:
        return requirements_file.read().split('\n')


setup(
    name='hyperstyle_analysis',
    version=get_version(),
    description='A set of analysis utilities for the Hyperstyle project.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/hyperskill/hyperstyle-analyze',
    author='Stepik.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    keywords='analysis',
    python_requires='>=3.8, <4',
    install_requires=get_requires(),
    packages=find_packages(exclude=[
        '*.unit_tests',
        '*.unit_tests.*',
        'unit_tests.*',
        'unit_tests',
    ]),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'analysis=src.python.evaluation.evaluation_run_tool:main',
        ],
    },
)
