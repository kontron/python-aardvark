Python binding for Totalphase Aardvark |BuildStatus|
====================================================

The `Totalphase`_ Aardvark is an USB |I2C|/SPI host adapter.


Rationale
=========

The manufacturer already provides an python binding. So why a new one? This
is correct, but the python binding you can find in the
``aardvark-linux-api`` package is very C oriented. Eg. you need to pass
arrays as method parameters, which are then modified by the binding.
Instead, this binding tries to be more pythonic.


Requirements
============

You need an either a x86 or an amd64 machine. This is because the binding
uses a binary-only module supplied by the manufacturer, Totalphase.
Additonally, only Linux is supported at the moment.


.. _Totalphase: http://www.totalphase.com
.. |I2C| replace:: I\ :sub:`2`\ C
.. |BuildStatus| image:: https://travis-ci.org/kontron/python-aardvark.png?branch=master
                 :target: https://travis-ci.org/kontron/python-aardvark
