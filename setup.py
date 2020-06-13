import sys

from setuptools import setup

__title__ = 'loguru-mypy'
__author__ = 'Tomasz Trębski'
__author_email__ = 'kornicameister@gmail.com'
__maintainer__ = __author__
__url__ = 'https://github.com/kornicameister/loguru-mypy'

if sys.version_info < (3, 6):
    raise RuntimeError('loguru-mypy requires Python 3.6 or greater')

setup(
    setup_requires='setupmeta',
    python_requires='>=3.6.0',
    versioning='post',
)
