#!/usr/bin/env python
#
# Totalphase Aardvark command line interface
#

import sys
import time
import logging
from optparse import OptionParser

from pyaardvark import Aardvark

def i2c_usage():
    print """
i2c wr <addr> <data>
i2c rd <addr> <length>
i2c wrrd <addr> <data> <length>
"""[1:-1]

def cmd_i2c(a, args):
    if len(args) < 1 or args[0] not in ('rd', 'wr', 'wrrd'):
        i2c_usage()
        sys.exit(1)

    (subcmd, args) = (args[0], args[1:])

    if subcmd == 'wr':
        if len(args) < 2:
            i2c_usage()
            sys.exit(1)

        try:
            i2c_address = int(args[0], 0)
            data = ''.join('%c' % chr(int(c, 0)) for c in args[1:])
        except ValueError:
            print 'could not convert arguments'
            sys.exit(1)

        a.i2c_master_write(i2c_address, data)
    elif subcmd == 'rd':
        if len(args) != 2:
            i2c_usage()
            sys.exit(1)

        try:
            i2c_address = int(args[0], 0)
            length = int(args[1], 0)
        except ValueError:
            print 'could not convert arguments'
            sys.exit(1)

        data = a.i2c_master_read(i2c_address, length)
        print ' '.join('%02x' % ord(c) for c in data)
    elif subcmd == 'wrrd':
        if len(args) < 3:
            i2c_usage()
            sys.exit(1)

        try:
            i2c_address = int(args[0], 0)
            data = ''.join('%c' % chr(int(c, 0)) for c in args[1:-1])
            length = int(args[-1], 0)
        except ValueError:
            print 'could not convert arguments'
            sys.exit(1)

        data = a.i2c_master_write_read(i2c_address, data, length)
        print ' '.join('%02x' % ord(c) for c in data)

def spi_usage():
    print """
spi <data> [<data>..]
"""[1:-1]

def cmd_spi(a, args):
    if len(args) < 1:
        spi_usage()
        sys.exit(1)

    try:
        data = ''.join('%c' % chr(int(c, 0)) for c in args)
    except ValueError:
        print 'could not convert arguments'
        sys.exit(1)

    data = a.spi_write(data)
    print ' '.join('%02x' % ord(c) for c in data)

def adt7420_usage():
    print "adt7420 <addr>"

def cmd_adt7420(a, args):
    if len(args) < 1:
        adt7420_usage()
        sys.exit(1)

    i2c_address = int(args[0], 0)

    data = a.i2c_master_write_read(i2c_address, '\x00', 2)

    temp = ord(data[0]) << 5
    temp |= ord(data[1]) >> 3

    if (temp & 0x1000):
        temp -= 8192
    print "%f (0x%02x%02x)" % (temp / 16.0, ord(data[0]), ord(data[1]))

def adt7411_usage():
    print "adt7411 <addr> enable"
    print "adt7411 <addr> int_diode"
    print "adt7411 <addr> ext_diode"

def cmd_adt7411(a, args):
    if len(args) < 2:
        adt7411_usage()
        sys.exit(1)

    i2c_address = int(args[0], 0)

    if args[1] == 'enable':
        a.i2c_master_write(i2c_address, '\x18\x0d')
        return
    elif args[1] == 'int_diode':
        lsb = a.i2c_master_write_read(i2c_address, '\x03', 1)
        msb = a.i2c_master_write_read(i2c_address, '\x07', 1)
    elif args[1] == 'ext_diode':
        lsb = a.i2c_master_write_read(i2c_address, '\x04', 1)
        msb = a.i2c_master_write_read(i2c_address, '\x08', 1)
    else:
        adt7411_usage()
        sys.exit(1)

    raw = ord(msb) << 2
    raw |= ord(lsb) & 0x3

    if (raw & 0x200):
        temp = raw - 1024
    else:
        temp = raw
    print "%f (0x%04x)" % (temp / 4.0, raw)

def main():
    usage = 'usage: %prog [options] <cmd> [..]'
    parser = OptionParser(usage=usage)
    parser.add_option('-b', '--bitrate',
            type='int',
            dest='bitrate',
            default=100,
            help='set bitrate in kHz')
    parser.add_option('-p', '--enable-i2c-pullups',
            action='store_true',
            dest='enable_i2c_pullups',
            help='enable I2C pullups')
    parser.add_option('--enable-target-power',
            action='store_true',
            dest='enable_target_power',
            help='enable target power (Be careful!)')
    parser.add_option('-d', '--device',
            type='int',
            dest='device',
            default=0,
            help='set device')
    parser.add_option('-v', action='store_true', dest='verbose',
            help='be more verbose')

    (options, args) = parser.parse_args()

    logging.basicConfig()
    if options.verbose:
        logging.getLogger('pyaardvark').setLevel(logging.DEBUG)

    if len(args) < 1:
        print parser.format_help()
        sys.exit(1)

    cmd = args[0]

    if cmd not in ('i2c', 'spi', 'adt7411', 'adt7420', 'scan'):
        print 'unknown command %s' % cmd
        sys.exit(1)

    if cmd == 'scan':
        for port in Aardvark.find_devices():
            dev = Aardvark()
            dev.open(port)
            id = dev.unique_id()
            id1 = id / 1000000
            id2 = id % 1000000
            print "Device #%d: %d-%d" % (port, id1, id2)
            dev.close()
        sys.exit(0)

    try:
        a = Aardvark()
        a.open(options.device)

        a.enable_target_power(options.enable_target_power)

        if cmd in ('i2c', 'adt7411', 'adt7420'):
            a.configure(Aardvark.CONFIG_SPI_I2C)
            a.i2c_enable_pullups(options.enable_i2c_pullups)
            a.i2c_bitrate(options.bitrate)
        if cmd == 'i2c':
            cmd_i2c(a, args[1:])
        elif cmd == 'spi':
            a.configure(Aardvark.CONFIG_SPI_I2C)
            a.spi_configure_mode(Aardvark.SPI_MODE_3)
            a.spi_bitrate(options.bitrate)
            cmd_spi(a, args[1:])
        elif cmd == 'adt7411':
            cmd_adt7411(a, args[1:])
        elif cmd == 'adt7420':
            cmd_adt7420(a, args[1:])
        else:
            pass
    except Exception, e:
        print e
    finally:
        a.close()

if __name__ == '__main__':
    main()
