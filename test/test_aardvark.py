#!/usr/bin/env python

import unittest
from mock import patch
from pyaardvark import Aardvark

@patch('pyaardvark.aardvark.api')
class AardvarkTest(unittest.TestCase):
    def setUp(self):
        self.a = Aardvark()

    def test_find_devices_valid_devices(self, api):
        def f(num, devices):
            devices[0] = 42
            devices[1] = 4711
            return 2

        api.py_aa_find_devices.side_effect = f
        devs = self.a.find_devices()
        self.assertEqual(devs[0], 42)
        self.assertEqual(devs[1], 4711)

    def test_find_devices_error(self, api):
        def f(num, devices):
            devices[0] = 42
            devices[1] = 4711
            return 2

        api.py_aa_find_devices.return_value = -10
        self.assertRaises(IOError, self.a.find_devices)

if __name__ == '__main__':
    unittest.main()
