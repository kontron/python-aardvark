#
# Aardvark Interface
#
# author: Michael Walle <michael.walle@kontron.com>
#

import time
import array
import logging

import ext.aardvark as api

log = logging.getLogger(__name__)

class Aardvark:
    """Represent an Aardvark device."""
    BUFFER_SIZE = 65535

    ERR_UNABLE_TO_LOAD_LIBRARY = -1
    ERR_UNABLE_TO_LOAD_DRIVER = -2
    ERR_UNABLE_TO_LOAD_FUNCTION = -3
    ERR_INCOMPATIBLE_LIBRARY = -4
    ERR_INCOMPATIBLE_DEVICE = -5
    ERR_COMMUNICATION_ERROR = -6
    ERR_UNABLE_TO_OPEN = -7
    ERR_UNABLE_TO_CLOSE = -8
    ERR_INVALID_HANDLE = -9
    ERR_CONFIG_ERROR = -10
    ERR_I2C_NOT_AVAILABLE = -100
    ERR_I2C_NOT_ENABLED = -101
    ERR_I2C_READ_ERROR = -102
    ERR_I2C_WRITE_ERROR = -103
    ERR_I2C_SLAVE_BAD_CONFIG = -104
    ERR_I2C_SLAVE_READ_ERROR = -105
    ERR_I2C_SLAVE_TIMEOUT = -106
    ERR_I2C_DROPPED_EXCESS_BYTES = -107
    ERR_I2C_BUS_ALREADY_FREE = -108
    ERR_SPI_NOT_AVAILABLE = -200
    ERR_SPI_NOT_ENABLED = -201
    ERR_SPI_WRITE_ERROR = -202
    ERR_SPI_SLAVE_READ_ERROR = -203
    ERR_SPI_SLAVE_TIMEOUT = -204
    ERR_SPI_DROPPED_EXCESS_BYTES = -205

    @staticmethod
    def _error_to_string(err):
        for attr in dir(Aardvark):
            if attr.startswith('ERR_'):
                if getattr(Aardvark, attr) == err:
                    return attr

    MAX_DEVICES = 16
    @staticmethod
    def find_devices():
        """Get a list of Aardvark devices.

        Returns the port number which can be used to open an Aardvark device.
        """
        # api expects array of u16
        devices = array.array('H', (0,) * Aardvark.MAX_DEVICES)
        ret = api.py_aa_find_devices(Aardvark.MAX_DEVICES, devices)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))
        del devices[ret:]
        return devices

    def __init__(self):
        self._handle = None

    def open(self, port=0):
        """Open an aardvark device.

        The port can be retrieved by `find_devices`. Usually, the first device
        is 0, the second 1, etc.

        If you are using only one device, you can therefore omit the parameter
        in which case 0 is used.
        """

        handle = api.py_aa_open(port)
        if handle <= 0:
            raise IOError('aardvark device on port %d not found' % port)

        self._handle = handle

    def close(self):
        """Close the device."""

        api.py_aa_close(self._handle)
        self._dev = None

    def unique_id(self):
        """Return the unique identifier of the device.

        That is, the serial number of the device as listed in the USB
        descriptor.
        """
        return api.py_aa_unique_id(self._handle)

    CONFIG_GPIO_ONLY = 0x00
    CONFIG_SPI_GPIO = 0x01
    CONFIG_GPIO_I2C = 0x02
    CONFIG_SPI_I2C = 0x03
    CONFIG_QUERY = 0x80

    def configure(self, config):
        """Configure the device.

        This enables I2C, SPI, GPIO, etc.
        """

        ret = api.py_aa_configure(self._handle, config)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))
        
    def i2c_bitrate(self, khz):
        """Set the I2C bitrate."""

        ret = api.py_aa_i2c_bitrate(self._handle, khz)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))
    
    I2C_PULLUP_NONE = 0x00
    I2C_PULLUP_BOTH = 0x03
    I2C_PULLUP_QUERY = 0x80
    def i2c_enable_pullups(self, enabled):
        """Enable I2C pullups."""

        if enabled:
            ret = api.py_aa_i2c_pullup(self._handle, self.I2C_PULLUP_BOTH)
        else:
            ret = api.py_aa_i2c_pullup(self._handle, self.I2C_PULLUP_NONE)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))

    TARGET_POWER_NONE = 0x00
    TARGET_POWER_BOTH = 0x03
    TARGET_POWER_QUERY = 0x80
    def enable_target_power(self, enabled):
        """Enable target power."""

        if enabled:
            power = self.TARGET_POWER_BOTH
        else:
            power = self.TARGET_POWER_NONE
        ret = api.py_aa_target_power(self._handle, power)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))

    I2C_NO_FLAGS = 0x00
    I2C_10_BIT_ADDR = 0x01
    I2C_COMBINED_FMT = 0x02
    I2C_NO_STOP = 0x04
    I2C_SIZED_READ = 0x10
    I2C_SIZED_READ_EXTRA1 = 0x20
    def i2c_master_write(self, i2c_address, data, flags=I2C_NO_FLAGS):
        """Make an I2C write access.

        The given I2C device is addressed and data given as a string is
        written. The transaction is finished with an I2C stop condition unless
        I2C_NO_STOP is set in the flags.

        10 bit addresses are supported if the I2C_10_BIT_ADDR flag is set.
        """

        data = array.array('B', data)
        ret = api.py_aa_i2c_write(self._handle, i2c_address,
                flags, len(data), data)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))

    def i2c_master_read(self, addr, length, flags=I2C_NO_FLAGS):
        """Make an I2C read access.

        The given I2C device is addressed and clock cycles for `length` bytes
        are generated. A short read will occur if the device generates an early
        NAK.

        The transaction is finished with an I2C stop condition unless the
        I2C_NO_STOP flag is set.
        """

        data = array.array('B', (0,) * length)
        ret = api.py_aa_i2c_read(self._handle, addr, flags, length,
                data)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))
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

        self.i2c_master_write(i2c_address, data, self.I2C_NO_STOP)
        return self.i2c_master_read(i2c_address, length)

    def i2c_slave_enable(self, slave_address):
        """Enable slave mode.

        The device will respond to the specified slave_address if it is
        addressed.

        You can wait for the data with `poll` and get it with
        `i2c_slave_read`.
        """
        ret = api.py_aa_i2c_slave_enable(self._handle, slave_address,
                self.BUFFER_SIZE, self.BUFFER_SIZE)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))

    POLL_NO_DATA = 0x00
    POLL_I2C_READ = 0x01
    POLL_I2C_WRITE = 0x02
    POLL_SPI = 0x04
    POLL_I2C_MONITOR = 0x08
    def poll(self, timeout_ms):
        """Wait for an event to occur.
        
        Returns a bitfield of event flags.
        """
        ret = api.py_aa_async_poll(self._handle, timeout_ms)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))
        return ret

    def i2c_slave_read(self):
        """Read the bytes from an I2C slave reception.
        
        The bytes are returns as an string object.
        """
        data = array.array('B', (0,) * self.BUFFER_SIZE)
        (ret, slave_addr) = api.py_aa_i2c_slave_read(self._handle, self.BUFFER_SIZE,
                data)
        if ret < 0:
            raise IOError(Aardvark._error_to_string(ret))
        del data[ret:]
        return (slave_addr, data.tostring())
