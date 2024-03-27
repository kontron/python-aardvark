import sys

if sys.platform.startswith('linux'):
    try:
        from .linux32 import aardvark as api
    except ImportError:
        try:
            from .linux64 import aardvark as api
        except ImportError:
            api = None
elif sys.platform.startswith('win32'):
    try:
        from .win32 import aardvark as api
    except ImportError:
        try:
            from .win64 import aardvark as api
        except ImportError:
            api = None
elif sys.platform.startswith('darwin'):
    try:
        from .osx64 import aardvark as api
    except ImportError:
        try:
            from .osxarm import aardvark as api
        except ImportError:
            api = None
else:
    api = None

if not api:
    raise RuntimeError('Unable to find suitable binary interface. '
            'Unsupported platform?')
