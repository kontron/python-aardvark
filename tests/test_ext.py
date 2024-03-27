#!/usr/bin/env python

import pyaardvark

def test_api_version():
    assert pyaardvark.api_version() == '6.00'
