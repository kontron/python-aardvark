#!/usr/bin/env python
#
# Totalphase Aardvark command line interface
#

import sys
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

    if cmd not in ('i2c', 'scan'):
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

        if cmd == 'i2c':
            a.configure(Aardvark.CONFIG_SPI_I2C)
            a.i2c_enable_pullups(options.enable_i2c_pullups)
            a.i2c_bitrate(options.bitrate)
            cmd_i2c(a, args[1:])
        else:
            pass
    except e:
        print e
    finally:
        a.close()

if __name__ == '__main__':
    main()
