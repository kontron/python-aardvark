"""
.. currentmodule:: pyaardvark

Most API functions will throw an :exc:`IOError` in case an error is
encountered. The :attr:`errno` attribute will set to one of the following
values:

.. data:: ERR_UNABLE_TO_LOAD_LIBRARY
.. data:: ERR_UNABLE_TO_LOAD_DRIVER
.. data:: ERR_UNABLE_TO_LOAD_FUNCTION
.. data:: ERR_INCOMPATIBLE_LIBRARY
.. data:: ERR_INCOMPATIBLE_DEVICE
.. data:: ERR_COMMUNICATION_ERROR
.. data:: ERR_UNABLE_TO_OPEN
.. data:: ERR_UNABLE_TO_CLOSE
.. data:: ERR_INVALID_HANDLE
.. data:: ERR_CONFIG_ERROR
.. data:: ERR_I2C_NOT_AVAILABLE
.. data:: ERR_I2C_NOT_ENABLED
.. data:: ERR_I2C_READ_ERROR
.. data:: ERR_I2C_WRITE_ERROR
.. data:: ERR_I2C_SLAVE_BAD_CONFIG
.. data:: ERR_I2C_SLAVE_READ_ERROR
.. data:: ERR_I2C_SLAVE_TIMEOUT
.. data:: ERR_I2C_DROPPED_EXCESS_BYTES
.. data:: ERR_I2C_BUS_ALREADY_FREE
.. data:: ERR_SPI_NOT_AVAILABLE
.. data:: ERR_SPI_NOT_ENABLED
.. data:: ERR_SPI_WRITE_ERROR
.. data:: ERR_SPI_SLAVE_READ_ERROR
.. data:: ERR_SPI_SLAVE_TIMEOUT
.. data:: ERR_SPI_DROPPED_EXCESS_BYTES

The functions :meth:`Aardvark.i2c_slave_read`, :meth:`Aardvark.i2c_master_read`
and :meth:`Aardvark.i2c_master_write` will throw an :exc:`IOError` with its
:attr:`errno` attribute set to a status code to indicate the state of the I2C
transaction in case of an error.

.. data:: I2C_STATUS_OK

    No error occured.

.. data:: I2C_STATUS_BUS_ERROR

    A bus error has occured. Transaction was aborted.

.. data:: I2C_STATUS_SLA_ACK

    Bus arbitration was lost during master transation; another master on the
    bus has successfully addressed this Aardvark adapter's slave address. As a
    result, this Aardvark adapter has automatically switched to slave mode and
    is responding.

.. data:: I2C_STATUS_SLA_NACK

    The Aardvark adapter failed to receive acknowledgement for the requested
    slave address during a master operation.

.. data:: I2C_STATUS_DATA_NACK

    The last data byte in the transaction was not acknowledged by the slave.

.. data:: I2C_STATUS_ARB_LOST

    I2C master arbitration lost, because another master on the bus was
    accessing the bus simultaneously.

.. data:: I2C_STATUS_BUS_LOCKED

    An I2C packet is in progress and the time since the last I2C event executed
    or received on the bus has exceeded the bus lock timeout. This is most
    likely due to the clock line of the bus being held low by some other device
    or due to the data line held low such that a start condition cannot be
    executed by the Aardvark adapter. The bus lock timeout can be configured
    using the :attr:`Aardvark.i2c_bus_timeout` property. The Aardvark adapter
    resets its own I2C interface when a timeout is observed and no further
    action is taken on the bus.

.. data:: I2C_STATUS_LAST_DATA_ACK

    The last byte was ACK'ed by the opposing master. When the Aardvark slave is
    configured with a fixed length transmit buffer, it will detach itself from
    the I2C bus after the buffer is fully transmitted and the aardvark slave
    also expects that the last byte sent from this buffer is NACK'ed by the
    opposing master device.

"""

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

PORT_NOT_FREE = 0x8000

CONFIG_GPIO_ONLY = 0x00
CONFIG_SPI_GPIO = 0x01
CONFIG_GPIO_I2C = 0x02
CONFIG_SPI_I2C = 0x03
CONFIG_QUERY = 0x80

I2C_NO_FLAGS = 0x00
I2C_10_BIT_ADDR = 0x01
I2C_COMBINED_FMT = 0x02
I2C_NO_STOP = 0x04
I2C_SIZED_READ = 0x10
I2C_SIZED_READ_EXTRA1 = 0x20

I2C_PULLUP_NONE = 0x00
I2C_PULLUP_BOTH = 0x03
I2C_PULLUP_QUERY = 0x80

TARGET_POWER_NONE = 0x00
TARGET_POWER_BOTH = 0x03
TARGET_POWER_QUERY = 0x80

POLL_NO_DATA = 0x00
POLL_I2C_READ = 0x01
POLL_I2C_WRITE = 0x02
POLL_SPI = 0x04
POLL_I2C_MONITOR = 0x08

I2C_MONITOR_NACK = 0x0100
I2C_MONITOR_START = 0xff00
I2C_MONITOR_STOP = 0xff01

I2C_STATUS_OK = 0
I2C_STATUS_BUS_ERROR = 1
I2C_STATUS_SLA_ACK = 2
I2C_STATUS_SLA_NACK = 3
I2C_STATUS_DATA_NACK = 4
I2C_STATUS_ARB_LOST = 5
I2C_STATUS_BUS_LOCKED = 6
I2C_STATUS_LAST_DATA_ACK = 7

SPI_POL_RISING_FALLING = 0
SPI_POL_FALLING_RISING = 1
SPI_PHASE_SAMPLE_SETUP = 0
SPI_PHASE_SETUP_SAMPLE = 1
SPI_BITORDER_MSB = 0
SPI_BITORDER_LSB = 1

SPI_MODE_0 = 0
SPI_MODE_3 = 3

SPI_SS_ACTIVE_LOW = 0
SPI_SS_ACTIVE_HIGH = 1
