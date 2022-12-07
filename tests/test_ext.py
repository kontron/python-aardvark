#!/usr/bin/env python

import nose
import pyaardvark
from nose.tools import eq_

def test_api_version():
    eq_(pyaardvark.api_version(), '5.70')

if __name__ == '__main__':
    nose.main()
