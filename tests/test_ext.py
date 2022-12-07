#!/usr/bin/env python

import pyaardvark

def test_api_version():
    assert pyaardvark.api_version() == '5.70'
