#!/usr/bin/env python

import array
import unittest
from mock import patch, call
from pyaardvark import Aardvark

@patch('pyaardvark.aardvark.api', autospec=True)
class AardvarkTest(unittest.TestCase):
    HANDLE = 42
    def setUp(self):
        self.a = Aardvark()
        self.a._handle = self.HANDLE

    def test_find_devices_valid_devices(self, api):
        def f(num, devices):
            devices[0] = 42
            devices[1] = 4711
            return 2

        api.py_aa_find_devices.side_effect = f
        devs = self.a.find_devices()
        self.assertEqual(devs[0], 42)
        self.assertEqual(devs[1], 4711)
        self.assertIsInstance(
                api.py_aa_find_devices.call_args[0][1], array.array)

    def test_find_devices_error(self, api):
        api.py_aa_find_devices.return_value = -1
        self.assertRaises(IOError, self.a.find_devices)

    def test_open_default(self, api):
        api.py_aa_open.return_value = 42
        self.a.open()
        self.assertEqual(self.a._handle, api.py_aa_open.return_value)

    def test_open_port(self, api):
        api.py_aa_open.return_value = 42
        self.a.open(4711)
        self.assertEqual(self.a._handle, api.py_aa_open.return_value)
        api.py_aa_open.assert_called_once_with(4711)

    def test_open_error(self, api):
        api.py_aa_open.return_value = -1
        self.assertRaises(IOError, self.a.open)

    def test_close(self, api):
        self.a.close()
        api.py_aa_close.assert_called_once_with(self.HANDLE)

    def test_unique_id(self, api):
        api.py_aa_unique_id.return_value = 3627028473
        unique_id = self.a.unique_id()
        api.py_aa_unique_id.assert_called_once_with(self.HANDLE)
        self.assertEqual(unique_id, api.py_aa_unique_id.return_value)

    def test_unique_id_str(self, api):
        api.py_aa_unique_id.return_value = 3627028473
        unique_id_str = self.a.unique_id_str()
        api.py_aa_unique_id.assert_called_once_with(self.HANDLE)
        self.assertEqual(unique_id_str, '3627-28473')

    def test_configure(self, api):
        api.py_aa_configure.return_value = 0
        self.a.configure(4711)
        api.py_aa_configure.assert_called_once_with(self.HANDLE, 4711)

    def test_configure_error(self, api):
        api.py_aa_configure.return_value = -1
        self.assertRaises(IOError, self.a.configure, (0,))

    def test_i2c_bitrate(self, api):
        api.py_aa_i2c_bitrate.return_value = 0
        self.a.i2c_bitrate(4711)
        api.py_aa_i2c_bitrate.assert_called_once_with(self.HANDLE, 4711)

    def test_i2c_bitrate_error(self, api):
        api.py_aa_i2c_bitrate.return_value = -1
        self.assertRaises(IOError, self.a.i2c_bitrate, (0,))

    def test_i2c_enable_pullups(self, api):
        api.py_aa_i2c_pullup.return_value = 0
        self.a.i2c_enable_pullups(False)
        self.a.i2c_enable_pullups(True)
        api.py_aa_i2c_pullup.assert_has_calls([
            call(self.HANDLE, Aardvark.I2C_PULLUP_NONE),
            call(self.HANDLE, Aardvark.I2C_PULLUP_BOTH),
        ])

    def test_i2c_enable_pullups_error(self, api):
        api.py_aa_i2c_pullup.return_value = -1
        self.assertRaises(IOError, self.a.i2c_enable_pullups, (0,))

    def test_enable_target_power(self, api):
        api.py_aa_target_power.return_value = 0
        self.a.enable_target_power(False)
        self.a.enable_target_power(True)
        api.py_aa_target_power.assert_has_calls([
            call(self.HANDLE, Aardvark.TARGET_POWER_NONE),
            call(self.HANDLE, Aardvark.TARGET_POWER_BOTH),
        ])

    def test_enable_target_power_error(self, api):
        api.py_aa_target_power.return_value = -1
        self.assertRaises(IOError, self.a.enable_target_power, (0,))

if __name__ == '__main__':
    unittest.main()
