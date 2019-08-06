from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

def read(*names, **kwargs):
    with io.open(
            join(dirname(__file__), *names),
            encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


setup(
    name='Python3 Chip8 Emulator',
    version='1.0',
    author='Sam Lastrina',
    long_description=open('readme.md').read(),
    install_requires=requirements,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    package_data = {'chip8': ['data/*']},
    zip_safe=False,
    python_requires='>=3.7',
    extras_require={},
    entry_points={
        'console_scripts': [
            'pyChip8SDL = chip8.app:main',
        ]
    },
)
