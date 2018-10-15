
.. include:: defines.rst.inc

Introduction
============

The :mod:`pyaardvark` module tries to provide a very simple API to use the
`Total Phase`_ Aardvark |I2C|/SPI Host adatper within your python program.

Simple Example
--------------

In this example we access an |I2C|-EEPROM on address `0x50` and read the
first five bytes of its content::

  import pyaardvark

  a = pyaardvark.open()
  data = a.i2c_master_write_read(0x50, '\x00', 5)
  # data = b'\x00\x01\x02\x03\x04'
  a.close()

Easy, huh?

For those, who are not familiar with |I2C|-EEPROM accesses: You first write
the offset to read from to the device (`0x00` in the example above) and
then you read the desired amount of bytes from the device. The offset
counter will automatically be incremened. Therefore, in the example above
you read the bytes at the offsets 0, 1, 2, 3 and 4. Please note, that there
are byte- and word-addressable EEPROMs. In this example we assumed a
byte-addressable one, because our offset is only one byte.

Tutorial
--------

Opening an Aardvark device
~~~~~~~~~~~~~~~~~~~~~~~~~~

You have three choices to open your Aardvark device. The first is the one
you saw in the simple example above::

  a = pyaardvark.open()

If you have only one device connected to your machine, this is all you have
to do. :func:`pyaardvark.open` automatically uses the first device it finds.

If you have multiple devices connected, you can either use the port
parameter::

  a = pyaardvark.open(1)

or the serial number, which you can find on the device itself or
in your USB properties of your machine::

  a = pyaardvark.open(serial_number='1111-222222')

In all cases :func:`pyaardvark.open` returns an
:class:`pyaardvark.Aardvark` object, which then can be used to access the
host adapter.

Using the context manager protocol to open an Aardvark device
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All methods of the :class:`pyaardvark.Aardvark` object can raise an
:exc:`IOError`. Instead of using *try .. except .. finally ..* you can use
the `with` statement to open the device. Closing the device will then
happen automatically after the block::

  with pyaardvark.open() as a:
      print a.api_version
  # no need for a.close() here

Accessing your |I2C| and SPI devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To issue |I2C| or SPI transactions you have to first configure the adapter
in the corresponding output mode. Each interface, |I2C| or SPI, can either
be GPIOs or the actual interface. So if, for example you want to use both
|I2C| and SPI at the same time and none of them as GPIOs::

  a.enable_i2c = True
  a.enable_spi = True

After you enabled the |I2C| interface you can issue transactions on the bus::

  a.i2c_master_write(0x50, b'\x00\x02\0x00\x00')

This will write adress device `0x50` and sends the byte sequence `0x00`,
`0x02`, `0x00`, `0x00` to it. To read from a device use
:meth:`pyaardvark.Aardvark.i2c_master_read`. Eventually, both can be combined
and issued in one transaction:
:meth:`pyaardvark.Aardvark.i2c_master_write_read`.


Closing the device
~~~~~~~~~~~~~~~~~~

Releasing the device can be done with :meth:`pyaardvark.Aardvark.close`::

  a.close()

FAQ
---

On pyaardvark datatypes
~~~~~~~~~~~~~~~~~~~~~~~

Most parameters of the API take bytes (eg.
:meth:`pyaardvark.Aardvark.i2c_master_write_read`). Former versions of
:mod:`pyaardvark` used strings, which where handled differently in Python 2
and Python 3. For this reason, :mod:`pyaardvark` now uses the bytes object
to encapsulate data. For Python 2 compatibility, the bytes backport is used
(:class:`newbytes`). This simplifies the data handling because you don't
have to explicitly convert the individual characters of the string to
integers (using :func:`ord`) anymore.

.. warning::

  Therefore the following is only valid for older :mod:`pyaardvark`
  versions (=< 0.5).

Iterables to strings using the built-in chr function::

  data = (0x01, 0xaf, 0xff)
  data = ''.join(chr(c) for c in data) # data is '\x01\xaf\xff'
  a.i2c_master_write(0x50, data)       # writes 1h, AFh, FFh to address 50h

To convert a character/string to a number you can use the build-in ord
function::

  data_str = a.i2c_master_read(0x50, 3) # data_str is '\xc0\x01\xff'
  data = [ord(b) for b in data_str]     # data is [192, 1, 255]
