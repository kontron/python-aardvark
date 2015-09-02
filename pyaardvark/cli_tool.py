#!/usr/bin/env python

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

from __future__ import print_function
import logging
import argparse
from functools import partial

import pyaardvark

int_base0 = partial(int, base=0)

def byte(value):
    msg = None
    try:
        value = int(value, 0)
        if value < 0 or value > 255:
            msg = '%d is not in range 0..255' % value
    except ValueError:
        msg = 'could not convert %r to a number' % value
    if msg is not None:
        raise argparse.ArgumentTypeError(msg)
    return value

def _i2c_common(a, args):
    a.enable_i2c = True
    a.i2c_pullups = args.enable_i2c_pullups
    a.i2c_bitrate = args.bitrate

def i2c_wr(a, args):
    _i2c_common(a, args)
    data = ''.join('%c' % c for c in args.data)
    a.i2c_master_write(args.i2c_address, data)

def i2c_wrrd(a, args):
    _i2c_common(a, args)
    data = ''.join('%c' % c for c in args.data)
    data = a.i2c_master_write_read(args.i2c_address, data, args.num_bytes)
    print(' '.join('%02x' % ord(c) for c in data))

def i2c_rd(a, args):
    _i2c_common(a, args)
    data = a.i2c_master_read(args.i2c_address, args.num_bytes)
    print(' '.join('%02x' % ord(c) for c in data))

def spi(a, args):
    a.enable_spi = True
    a.spi_configure_mode(pyaardvark.SPI_MODE_3)
    a.spi_bitrate = args.bitrate
    data = ''.join('%c' % c for c in args.data)
    data = a.spi_write(data)
    print(' '.join('%02x' % ord(c) for c in data))

def scan(a, args):
    for dev in pyaardvark.find_devices():
        dev['in_use'] = ' [IN USE]' if dev['in_use'] else ''
        print('Device #%(port)d: %(serial_number)s%(in_use)s' % dev)

def monitor(a, args):
    def data_to_str(d):
        if d == pyaardvark.I2C_MONITOR_START:
            return 'STA'
        elif d == pyaardvark.I2C_MONITOR_STOP:
            return 'STP\n'
        elif d == pyaardvark.I2C_MONITOR_NACK:
            return '*'
        else:
            return '%02x' % d

    a.enable_i2c_monitor()
    try:
        while True:
            a.poll()
            data = a.i2c_monitor_read()
            data = map(data_to_str, data)
            print(*data, end='')
    except KeyboardInterrupt:
        print()

def main(args=None):
    parser = argparse.ArgumentParser(
            description='Total Phase I2C/SPI host adapter CLI.')
    parser.add_argument('-v', action='store_true', dest='verbose',
            help='be more verbose')
    parser.add_argument('-d', '--device', type=int, dest='device', default=0,
            help='set device number')
    parser.add_argument('-s', '--serial-number', type=str,
            dest='serial_number', default=None,
            help='set serial number. Takes precedence over port number.')
    parser.add_argument('-b', '--bitrate', type=int, dest='bitrate',
            default=100, help='set bitrate in kHz')
    parser.add_argument('-p', '--enable-i2c-pullups', action='store_true',
            dest='enable_i2c_pullups', help='enable I2C pullups')
    parser.add_argument('-P', '--enable-target-power', action='store_true',
            dest='enable_target_power',
            help='enable target power (Be careful!)')

    _sub = parser.add_subparsers(title='Commands')

    # scan sub command
    subparser = _sub.add_parser('scan',
            help='Find attached Aardvark devices')
    subparser.set_defaults(func=scan)

    # monitor sub command
    subparser = _sub.add_parser('monitor', help='Listen on I2C bus')
    subparser.set_defaults(func=monitor)

    # spi subcommand
    subparser = _sub.add_parser('spi', help='SPI commands')
    subparser.add_argument('data', nargs='+', type=byte, metavar="DATA",
            help='byte to write')
    subparser.set_defaults(func=spi)

    # i2c subcommand
    subparser = _sub.add_parser('i2c', help='I2C commands')

    # i2c wr
    _sub_i2c = subparser.add_subparsers()
    subparser = _sub_i2c.add_parser('wr', help='write transaction')
    subparser.add_argument('i2c_address', type=byte, metavar="ADDR",
            help='I2C slave address')
    subparser.add_argument('data', nargs='+', type=byte, metavar="DATA",
            help='byte to write')
    subparser.set_defaults(func=i2c_wr)

    # i2c rd
    subparser = _sub_i2c.add_parser('rd', help='read transaction')
    subparser.add_argument('i2c_address', type=byte, metavar="ADDR",
            help='I2C slave address')
    subparser.add_argument('num_bytes', type=int_base0, metavar="NUM_BYTES",
            help='number of bytes to read')
    subparser.set_defaults(func=i2c_rd)

    # i2c wrrd
    subparser = _sub_i2c.add_parser('wrrd',
            help='write/read transaction')
    subparser.add_argument('i2c_address', type=byte, metavar="ADDR",
            help='I2C slave address')
    subparser.add_argument('num_bytes', type=int_base0, metavar="NUM_BYTES",
            help='number of bytes to read')
    subparser.add_argument('data', nargs='+', type=byte, metavar="DATA",
            help='byte to write')
    subparser.set_defaults(func=i2c_wrrd)

    args = parser.parse_args(args)

    logging.basicConfig()
    if args.verbose:
        logging.getLogger('pyaardvark').setLevel(logging.DEBUG)

    a = None
    ret = 0
    try:
        if args.func != scan:
            a = pyaardvark.open(args.device, serial_number=args.serial_number)
            a.target_power = args.enable_target_power

        args.func(a, args)
    except IOError as e:
        print(e)
        ret = 1
    finally:
        if a is not None:
            a.close()

    return ret

if __name__ == '__main__':
    main()
