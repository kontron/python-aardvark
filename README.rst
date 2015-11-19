Python binding for Total Phase Aardvark
=======================================

|BuildStatus| |PyPiVersion|

The `Total Phase`_ Aardvark is an USB |I2C|/SPI host adapter.


Rationale
---------

The manufacturer already provides an python binding. So why a new one? This
is correct, but the python binding you can find in the
``aardvark-linux-api`` package is very C oriented. Eg. you need to pass
arrays as method parameters, which are then modified by the binding.
Instead, this binding tries to be more pythonic.


Features
--------

* simple interface
* CLI tool for easy testing
* |I2C| and SPI support
* support for control signals like target power and internal |I2C| pullups
* rudimental |I2C| slave support
* Support for Linux, Windows and OSX


(Still) Missing Features
------------------------

* more documentation (please bear with me)
* GPIO support


Documentation
-------------

You can find the most up to date documentation at:
http://pyaardvark.rtfd.org


Requirements
------------

You need an either a x86 or an amd64 machine. This is because the binding
uses a binary-only module supplied by the manufacturer, Total Phase.
Linux, Windows, and OSX is supported.


Contributing
------------

Contributions are always welcome. You may send patches directly (eg. ``git
send-email``), do a github pull request or just file an issue.

If you are doing code changes or additions please:

* respect the coding style (eg. PEP8),
* provide well-formed commit message (see `this blog post
  <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.)
* add a Signed-off-by line (eg. ``git commit -s``)


License
-------

This library is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2.1 of the License, or (at
your option) any later version.

This library is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this library; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

.. _Total Phase: http://www.totalphase.com
.. |I2C| replace:: I\ :sup:`2`\ C
.. |BuildStatus| image:: https://travis-ci.org/kontron/python-aardvark.png?branch=master
                 :target: https://travis-ci.org/kontron/python-aardvark
.. |PyPiVersion| image:: https://badge.fury.io/py/pyaardvark.svg
                 :target: http://badge.fury.io/py/pyaardvark
