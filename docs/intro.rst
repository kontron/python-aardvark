
.. include:: defines.rst.inc

Introduction
============

The :mod:`pyaardvark` module tries to provide a very simple API to use the
`Total Phase`_ Aardvark |I2C|/SPI Host adatper within your python program.

Simple Example
--------------

In this example we access an (byte-addressable) |I2C|-EEPROM on address
0x50 and read the first five bytes of its content::

  import pyaardvark

  a = pyaardvark.open()
  data = a.i2c_master_write_read(0x50, '\x00', 5)
  # data = '\x00\x01\x02\x03\x04'
  a.close()

Easy, huh?


Tutorial
--------

Opening an Aardvark device
~~~~~~~~~~~~~~~~~~~~~~~~~~

You have three choices to open your Aardvark device. The first is the one
you saw in the simple example above::

  >>> a = pyaardvark.open()

If you have only one device connected to your machine, this is all you have
to do. :func:`pyaardvark.open` automatically uses the first device it finds.

If you have multiple devices connected, you can either use the port
parameter::

  >>> a = pyaardvark.open(1)

or the serial number, which you can find on the device itself or
in your USB properties of your machine::

  >>> a = pyaardvark.open(serial_number='1111-222222')

