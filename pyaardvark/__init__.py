try:
    from version import __version__
except ImportError:
    __version__ = 'dev'

from aardvark import Aardvark
