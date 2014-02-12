# Copyright (c) 2014  Kontron Europe GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import time
import array
import logging

from .constants import *

try:
    import ext.linux32.aardvark as api
except ImportError:
    try:
        import ext.linux64.aardvark as api
    except:
        api = None

log = logging.getLogger(__name__)

def error_string(error_number):
    for k, v in globals().items():
        if k.startswith('ERR_') and v == error_number:
            return k
    else:
        return 'ERR_UNKNOWN_ERROR'

def find_devices(filter_in_use=True):
    """Return a list of port numbers which can be used with :func:`open`.

    If *filter_in_use* parameter is `True` devices which are already opened
    will be filtered from the list. If set to `False`, the port numbers are
    still included in the returned list and the user may get an
    :class:`IOError` if the port number is used with :func:`open`.

    .. note::

       There is no guarantee, that the returned port numbers are still valid
       when you open the device with it. Eg. it may be disconnected from the
       machine after you call :func:`find_devices` but before you call
       :func:`open`.
    """

    # first fetch the number of attached devices, so we can create a buffer
    # with the exact amount of entries. api expects array of u16
    num_devices = api.py_aa_find_devices(0, array.array('H'))
    assert num_devices > 0

    devices = array.array('H', (0,) * num_devices)
    num_devices = api.py_aa_find_devices(len(devices), devices)
    assert num_devices > 0

    del devices[num_devices:]

    if filter_in_use:
        devices = [ d for d in devices if not d & PORT_NOT_FREE ]
    else:
        devices = [ d & ~PORT_NOT_FREE for d in devices]
    return devices

def open(port=None, serial_number=None):
    """Open an aardvark device and return an :class:`Aardvark` object. If the
    device cannot be opened an :class:`IOError` is raised.

    The `port` can be retrieved by :func:`find_devices`. Usually, the first
    device is 0, the second 1, etc.

    If you are using only one device, you can therefore omit the parameter
    in which case 0 is used.

    Another method to open a device is to use the serial number. You can either
    find the number on the device itself or in the in the corresponding USB
    property. The serial number is a string which looks like `NNNN-MMMMMMM`.

    Raises an :class:`IOError` if the port number (or serial number) does not
    exist, is already connected or an incompatible device is found.
    """
    if port is None and serial_number is None:
        dev = Aardvark()
    elif serial_number is not None:
        for port in find_devices():
            dev = Aardvark(port)
            if dev.unique_id_str() == serial_number:
                break
            dev.close()
        else:
            raise IOError(error_string(ERR_UNABLE_TO_OPEN))
    else:
        dev = Aardvark(port)

    return dev

class Aardvark:
    """Represents an Aardvark device."""
    BUFFER_SIZE = 65535

    def __init__(self, port=0):
        self.handle = api.py_aa_open(port)
        if self.handle <= 0:
            raise IOError(error_string(self.handle))

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()
        return False

    def close(self):
        """Close the device."""

        api.py_aa_close(self.handle)
        self.handle = None

    def unique_id(self):
        """Return the unique identifier of the device. The identifier is the
        serial number you can find on the adapter without the dash. Eg. the
        serial number 0012-345678 would be 12345678.
        """
        return api.py_aa_unique_id(self.handle)

    def unique_id_str(self):
        """Return the unique identifier. But unlike :func:`unique_id`, the ID
        is returned as a string which has the format NNNN-MMMMMMM.
        """
        unique_id = self.unique_id()
        id1 = unique_id / 1000000
        id2 = unique_id % 1000000
        return '%04d-%06d' % (id1, id2)

    def configure(self, config):
        """Configure the mode of the aardvark device.

        The hardware supports the following mode:

        ====== ======
          #1     #2
        ====== ======
         GPIO   GPIO
         SPI    GPIO
         GPIO   I2C
         SPI    I2C
        ====== ======

        That is, if the hardware interface (either SPI or I2C) is disabled,
        this port is automatically in GPIO mode.
        """

        ret = api.py_aa_configure(self.handle, config)
        if ret < 0:
            raise IOError(error_string(ret))

    def i2c_bitrate(self, khz):
        """Set the I2C bitrate."""

        ret = api.py_aa_i2c_bitrate(self.handle, khz)
        if ret < 0:
            raise IOError(error_string(ret))

    def i2c_enable_pullups(self, enabled):
        """Enable I2C pullups."""

        if enabled:
            pullup = I2C_PULLUP_BOTH
        else:
            pullup = I2C_PULLUP_NONE
        ret = api.py_aa_i2c_pullup(self.handle, pullup)
        if ret < 0:
            raise IOError(error_string(ret))

    def enable_target_power(self, enabled):
        """Enable target power."""

        if enabled:
            power = TARGET_POWER_BOTH
        else:
            power = TARGET_POWER_NONE
        ret = api.py_aa_target_power(self.handle, power)
        if ret < 0:
            raise IOError(error_string(ret))

    def i2c_master_write(self, i2c_address, data, flags=I2C_NO_FLAGS):
        """Make an I2C write access.

        The given I2C device is addressed and data given as a string is
        written. The transaction is finished with an I2C stop condition unless
        I2C_NO_STOP is set in the flags.

        10 bit addresses are supported if the I2C_10_BIT_ADDR flag is set.
        """

        data = array.array('B', data)
        ret = api.py_aa_i2c_write(self.handle, i2c_address,
                flags, len(data), data)
        if ret < 0:
            raise IOError(error_string(ret))

    def i2c_master_read(self, addr, length, flags=I2C_NO_FLAGS):
        """Make an I2C read access.

        The given I2C device is addressed and clock cycles for `length` bytes
        are generated. A short read will occur if the device generates an early
        NAK.

        The transaction is finished with an I2C stop condition unless the
        I2C_NO_STOP flag is set.
        """

        data = array.array('B', (0,) * length)
        ret = api.py_aa_i2c_read(self.handle, addr, flags, length,
                data)
        if ret < 0:
            raise IOError(error_string(ret))
        del data[ret:]
        return data.tostring()

    def i2c_master_write_read(self, i2c_address, data, length):
        """Make an I2C write/read access.

        First an I2C write access is issued. No stop condition will be
        generated. Instead the read access begins with a repeated start.

        This method is useful for accessing most addressable I2C devices like
        EEPROMs, port expander, etc.

        Basically, this is just a convinient function which interally uses
        `i2c_master_write` and `i2c_master_read`.
        """

        self.i2c_master_write(i2c_address, data, I2C_NO_STOP)
        return self.i2c_master_read(i2c_address, length)

    def i2c_slave_enable(self, slave_address):
        """Enable slave mode.

        The device will respond to the specified slave_address if it is
        addressed.

        You can wait for the data with `poll` and get it with
        `i2c_slave_read`.
        """
        ret = api.py_aa_i2c_slave_enable(self.handle, slave_address,
                self.BUFFER_SIZE, self.BUFFER_SIZE)
        if ret < 0:
            raise IOError(error_string(ret))

    def poll(self, timeout_ms):
        """Wait for an event to occur.

        Returns a bitfield of event flags.
        """
        ret = api.py_aa_async_poll(self.handle, timeout_ms)
        if ret < 0:
            raise IOError(error_string(ret))
        return ret

    def i2c_slave_read(self):
        """Read the bytes from an I2C slave reception.

        The bytes are returns as an string object.
        """
        data = array.array('B', (0,) * self.BUFFER_SIZE)
        (ret, slave_addr) = api.py_aa_i2c_slave_read(self.handle, self.BUFFER_SIZE,
                data)
        if ret < 0:
            raise IOError(error_string(ret))
        del data[ret:]
        return (slave_addr, data.tostring())

    def spi_bitrate(self, khz):
        """Set the SPI bitrate."""
        ret = api.py_aa_spi_bitrate(self.handle, khz)
        if ret < 0:
            raise IOError(error_string(ret))

    def spi_configure(self, polarity, phase, bitorder):
        """Configure the SPI interface."""
        ret = api.py_aa_spi_configure(self.handle, polarity, phase, bitorder)
        if ret < 0:
            raise IOError(error_string(ret))

    def spi_configure_mode(self, spi_mode):
        """Configure the SPI interface by the well known SPI modes."""
        if spi_mode == SPI_MODE_0:
            self.spi_configure(SPI_POL_RISING_FALLING,
                    SPI_PHASE_SAMPLE_SETUP, SPI_BITORDER_MSB)
        elif spi_mode == SPI_MODE_3:
            self.spi_configure(SPI_POL_FALLING_RISING,
                    SPI_PHASE_SETUP_SAMPLE, SPI_BITORDER_MSB)
        else:
            raise RuntimeError('SPI Mode not supported')

    def spi_write(self, data):
        "Write a stream of bytes to a SPI device."""
        data_out = array.array('B', data)
        data_in = array.array('B', (0,) * len(data_out))
        ret = api.py_aa_spi_write(self.handle, len(data_out), data_out,
                len(data_in), data_in)
        if ret < 0:
            raise IOError(error_string(ret))
        return data_in.tostring()

    def spi_ss_polarity(self, polarity):
        """Change the ouput polarity on the SS line.

        Please note, that this only affects the master functions.
        """
        ret = api.py_aa_spi_master_ss_polarity(self.handle, polarity)
        if ret < 0:
            raise IOError(error_string(ret))
