#!/usr/bin/env python

import array
import unittest
from mock import patch, call, ANY
import pyaardvark

@patch('pyaardvark.aardvark.api', autospec=True)
class AardvarkTest(unittest.TestCase):

    def open(self, api):
        api.py_aa_open.return_value = 1
        return pyaardvark.open()

    def test_error_string(self, api):
        self.assertEqual(pyaardvark.aardvark.error_string(-1),
                'ERR_UNABLE_TO_LOAD_LIBRARY')

    def test_error_string_invalid_num(self, api):
        self.assertEqual(pyaardvark.aardvark.error_string(1),
                'ERR_UNKNOWN_ERROR')

    def test_find_devices_valid_devices(self, api):
        def f(num, devices):
            devices[0] = 42
            devices[1] = 4711
            return 2

        api.py_aa_find_devices.side_effect = f
        devs = pyaardvark.find_devices()
        self.assertEqual(devs[0], 42)
        self.assertEqual(devs[1], 4711)
        self.assertIsInstance(
                api.py_aa_find_devices.call_args[0][1], array.array)

    def test_find_devices_error(self, api):
        api.py_aa_find_devices.return_value = -1
        self.assertRaises(IOError, pyaardvark.find_devices)

    def test_open_default(self, api):
        api.py_aa_open.return_value = 42
        a = pyaardvark.open()
        api.py_aa_open.assert_called_once_with(0)
        self.assertEqual(a.handle, api.py_aa_open.return_value)

    def test_open_port(self, api):
        api.py_aa_open.return_value = 42
        a = pyaardvark.open(4711)
        api.py_aa_open.assert_called_once_with(4711)
        self.assertEqual(a.handle, api.py_aa_open.return_value)

    def test_open_serial_number(self, api):
        devices = {
                42: 1234567890,
                4711: 1111222222,
                5: 3333444444,
        }
        def find_devices(_num, devs):
            for i, dev in enumerate(devices.keys()):
                devs[i] = dev
            return len(devices)

        def open(handle):
            return handle

        def unique_id(handle):
            return devices[handle]

        api.py_aa_find_devices.side_effect = find_devices
        api.py_aa_open.side_effect = open
        api.py_aa_unique_id.side_effect = unique_id

        a = pyaardvark.open(serial_number='1234-567890')
        self.assertEqual(a.handle, 42)

        a = pyaardvark.open(serial_number='1111-222222')
        self.assertEqual(a.handle, 4711)

        self.assertRaises(IOError, pyaardvark.open, serial_number='7777-888888')

    def test_open_error(self, api):
        api.py_aa_open.return_value = -1
        self.assertRaises(IOError, pyaardvark.open)

    def test_close(self, api):
        a = self.open(api)
        handle = a.handle
        a.close()
        api.py_aa_close.assert_called_once_with(handle)

    def test_unique_id(self, api):
        a = self.open(api)
        api.py_aa_unique_id.return_value = 3627028473
        unique_id = a.unique_id()
        api.py_aa_unique_id.assert_called_once_with(a.handle)
        self.assertEqual(unique_id, api.py_aa_unique_id.return_value)

    def test_unique_id_str(self, api):
        a = self.open(api)
        api.py_aa_unique_id.return_value = 627008473
        unique_id_str = a.unique_id_str()
        api.py_aa_unique_id.assert_called_once_with(a.handle)
        self.assertEqual(unique_id_str, '0627-008473')

    def test_configure(self, api):
        a = self.open(api)
        api.py_aa_configure.return_value = 0
        a.configure(4711)
        api.py_aa_configure.assert_called_once_with(a.handle, 4711)

    def test_configure_error(self, api):
        a = self.open(api)
        api.py_aa_configure.return_value = -1
        self.assertRaises(IOError, a.configure, (0,))

    def test_i2c_bitrate(self, api):
        a = self.open(api)
        api.py_aa_i2c_bitrate.return_value = 0
        a.i2c_bitrate(4711)
        api.py_aa_i2c_bitrate.assert_called_once_with(a.handle, 4711)

    def test_i2c_bitrate_error(self, api):
        a = self.open(api)
        api.py_aa_i2c_bitrate.return_value = -1
        self.assertRaises(IOError, a.i2c_bitrate, (0,))

    def test_i2c_enable_pullups(self, api):
        a = self.open(api)
        api.py_aa_i2c_pullup.return_value = 0
        a.i2c_enable_pullups(False)
        a.i2c_enable_pullups(True)
        api.py_aa_i2c_pullup.assert_has_calls([
            call(a.handle, pyaardvark.I2C_PULLUP_NONE),
            call(a.handle, pyaardvark.I2C_PULLUP_BOTH),
        ])

    def test_i2c_enable_pullups_error(self, api):
        a = self.open(api)
        api.py_aa_i2c_pullup.return_value = -1
        self.assertRaises(IOError, a.i2c_enable_pullups, (0,))

    def test_enable_target_power(self, api):
        a = self.open(api)
        api.py_aa_target_power.return_value = 0
        a.enable_target_power(False)
        a.enable_target_power(True)
        api.py_aa_target_power.assert_has_calls([
            call(a.handle, pyaardvark.TARGET_POWER_NONE),
            call(a.handle, pyaardvark.TARGET_POWER_BOTH),
        ])

    def test_enable_target_power_error(self, api):
        a = self.open(api)
        api.py_aa_target_power.return_value = -1
        self.assertRaises(IOError, a.enable_target_power, (0,))

    def test_i2c_master_write(self, api):
        a = self.open(api)
        addr = 0x50
        data = b'\x01\x02\x03'
        flags = pyaardvark.I2C_NO_STOP | pyaardvark.I2C_SIZED_READ
        api.py_aa_i2c_write.return_value = 0
        a.i2c_master_write(addr, data, flags)
        api.py_aa_i2c_write.assert_called_once_with(
                a.handle, addr, flags, len(data), array.array('B', data))

    def test_i2c_master_write_default_flags(self, api):
        a = self.open(api)
        api.py_aa_i2c_write.return_value = 0
        a.i2c_master_write(0, '')
        api.py_aa_i2c_write.assert_called_once_with(
                ANY, ANY, pyaardvark.I2C_NO_FLAGS, ANY, ANY)

    def test_i2c_master_write_error(self, api):
        a = self.open(api)
        api.py_aa_i2c_write.return_value = -1
        self.assertRaises(IOError, a.i2c_master_write, 0, '')

    def test_i2c_master_read(self, api):
        def i2c_master_read(_handle, _addr, _flags, length, data):
            self.assertEqual(data, array.array('B', (0,) * length))
            for i in range(length):
                data[i] = i
            return length

        a = self.open(api)
        addr = 0x50
        flags = pyaardvark.I2C_NO_STOP | pyaardvark.I2C_SIZED_READ
        api.py_aa_i2c_read.side_effect = i2c_master_read
        data = a.i2c_master_read(addr, 3, flags)
        api.py_aa_i2c_read.assert_called_once_with(
                a.handle, addr, flags, 3, ANY)
        self.assertEqual(data, b'\x00\x01\x02')

    def test_i2c_master_read_default_flags(self, api):
        a = self.open(api)
        api.py_aa_i2c_read.return_value = 1
        data = a.i2c_master_read(0, 0)
        api.py_aa_i2c_read.assert_called_once_with(
                ANY, ANY, pyaardvark.I2C_NO_FLAGS, ANY, ANY)

    def test_i2c_master_read_error(self, api):
        a = self.open(api)
        api.py_aa_i2c_read.return_value = -1
        self.assertRaises(IOError, a.i2c_master_read, 0, 0)

    def test_i2c_master_write_read(self, api):
        def i2c_master_read(_handle, _addr, _flags, length, data):
            self.assertEqual(data, array.array('B', (0,) * length))
            for i in range(length):
                data[i] = i
            return length

        a = self.open(api)
        api.py_aa_i2c_write.return_value = 0
        api.py_aa_i2c_read.side_effect = i2c_master_read
        addr = 0x50
        data = a.i2c_master_write_read(addr, b'\x00\x01\x02', 3)
        api.py_aa_i2c_write.assert_called_once_with(a.handle, addr,
                pyaardvark.I2C_NO_STOP, len(data), array.array('B', data))
        api.py_aa_i2c_read.assert_called_once_with(
                a.handle, addr, pyaardvark.I2C_NO_FLAGS, 3, ANY)
        self.assertEqual(data, b'\x00\x01\x02')

    def test_i2c_master_write_read_default_flags(self, api):
        a = self.open(api)
        api.py_aa_i2c_read.return_value = 1
        data = a.i2c_master_read(0, 0)
        api.py_aa_i2c_read.assert_called_once_with(
                ANY, ANY, pyaardvark.I2C_NO_FLAGS, ANY, ANY)

    def test_i2c_master_write_read_error_read(self, api):
        a = self.open(api)
        api.py_aa_i2c_write.return_value = 1
        api.py_aa_i2c_read.return_value = -1
        self.assertRaises(IOError, a.i2c_master_write_read, 0, '', 0)

    def test_i2c_master_write_read_error_write(self, api):
        a = self.open(api)
        api.py_aa_i2c_write.return_value = -1
        api.py_aa_i2c_read.return_value = 1
        self.assertRaises(IOError, a.i2c_master_write_read, 0, '', 0)

    def test_spi_bitrate(self, api):
        a = self.open(api)
        api.py_aa_spi_bitrate.return_value = 0
        a.spi_bitrate(4711)
        api.py_aa_spi_bitrate.assert_called_once_with(a.handle, 4711)

    def test_spi_bitrate_error(self, api):
        a = self.open(api)
        api.py_aa_spi_bitrate.return_value = -1
        self.assertRaises(IOError, a.spi_bitrate, (0,))

    def test_spi_configure(self, api):
        a = self.open(api)
        api.py_aa_spi_configure.return_value = 0
        a.spi_configure(1, 2, 3)
        api.py_aa_spi_configure.assert_called_once_with(a.handle, 1, 2, 3)

    def test_spi_configure_error(self, api):
        a = self.open(api)
        api.py_aa_spi_configure.return_value = -1
        self.assertRaises(IOError, a.spi_configure, 0, 0, 0)

    def test_spi_configure_mode_0(self, api):
        a = self.open(api)
        api.py_aa_spi_configure.return_value = 0
        a.spi_configure_mode(pyaardvark.SPI_MODE_0)
        api.py_aa_spi_configure.assert_called_once_with(a.handle, 0, 0, 0)

    def test_spi_configure_mode_3(self, api):
        a = self.open(api)
        api.py_aa_spi_configure.return_value = 0
        a.spi_configure_mode(pyaardvark.SPI_MODE_3)
        api.py_aa_spi_configure.assert_called_once_with(a.handle, 1, 1, 0)

    def test_spi_configure_mode_error(self, api):
        a = self.open(api)
        api.py_aa_spi_configure.return_value = -1
        self.assertRaises(IOError, a.spi_configure_mode, 0)

    def test_spi_configure_mode_unknown_mode(self, api):
        a = self.open(api)
        self.assertRaises(RuntimeError, a.spi_configure_mode, 1)

    def test_spi_ss_polarity(self, api):
        a = self.open(api)
        api.py_aa_spi_master_ss_polarity.return_value = 0
        a.spi_ss_polarity(42)
        api.py_aa_spi_master_ss_polarity.assert_called_once_with(a.handle, 42)

    def test_spi_ss_polarity_error(self, api):
        a = self.open(api)
        api.py_aa_spi_master_ss_polarity.return_value = -1
        self.assertRaises(IOError, a.spi_ss_polarity, 0)

    def test_spi_spi_write(self, api):
        def spi_write(_handle, len_tx, tx, len_rx, rx):
            self.assertEqual(len_tx, len_rx)
            for i, v in enumerate(reversed(tx)):
                rx[i] = v
            return len_tx
        a = self.open(api)
        api.py_aa_spi_write.side_effect = spi_write
        data = b'\x01\x02\x03'
        rx_data = a.spi_write(data)
        self.assertEqual(rx_data, data[::-1])
        api.py_aa_spi_write.assert_called_once_with(a.handle, len(data),
                array.array('B', data), len(data), ANY)

    def test_spi_spi_write_error(self, api):
        a = self.open(api)
        api.py_aa_spi_write.return_value = -1
        self.assertRaises(IOError, a.spi_write, '')

if __name__ == '__main__':
    unittest.main()
