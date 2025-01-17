#!/usr/bin/python
# coding=UTF-8

# ----------------------------------------------------------------------------
#
#   DRCONTROL.PY
#
#   Copyright (C) 2012 Sebastian Sjoholm, sebastian.sjoholm@gmail.com
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   Original Version history can be found at
#   http://code.google.com/p/drcontrol/wiki/VersionHistory
#
#
# ----------------------------------------------------------------------------

from optparse import OptionParser

from pylibftdi import Driver
from pylibftdi import BitBangDevice

from ctypes.util import find_library

import sys
import time

# ----------------------------------------------------------------------------
# VARIABLE CLASSS
# ----------------------------------------------------------------------------

class app_data:
    def __init__(
        self,
        name = "DRControl",
        version = "0.13",
        date = "$Date: 2013-01-03 18:13:01 +0100 (Thu, 03 Jan 2013) $",
        rev = "$Rev: 53 $",
        author = "Sebastian Sjoholm"
        ):

        self.name = name
        self.version = version
        self.build = date
        self.rev = rev
        self.author = author

class cmdarg_data:
    def __init__(
        self,
        device = "",
        relay = "",
        command = "",
        verbose = False
        ):

        self.device = device
        self.relay = relay
        self.command = command
        self.verbose = verbose

class relay_data(dict):

    address = {
            "1":"1",
            "2":"2",
            "3":"4",
            "4":"8",
            "all":"F"
            }

    def __getitem__(self, key): return self[key]
    def keys(self): return self.keys()

# ----------------------------------------------------------------------------
# testBit() returns a nonzero result, 2**offset, if the bit at 'offset' is one.
# http://wiki.python.org/moin/BitManipulation
# ----------------------------------------------------------------------------

def testBit(int_type, offset):
    mask = 1 << offset
    return(int_type & mask)

def get_relay_state( data, relay ):
    if relay == "1":
        return testBit(data, 1)
    if relay == "2":
        return testBit(data, 3)
    if relay == "3":
        return testBit(data, 5)
    if relay == "4":
        return testBit(data, 7)
    if relay == "5":
        return testBit(data, 2)
    if relay == "6":
        return testBit(data, 4)
    if relay == "7":
        return testBit(data, 6)
    if relay == "8":
        return testBit(data, 8)

# ----------------------------------------------------------------------------
# LIST_DEVICES()
#
# Routine modified from the original pylibftdi example by Ben Bass
# ----------------------------------------------------------------------------

def list_devices():
    result = []
    for device in Driver().list_devices():
        device = map(lambda x: x.decode('latin1') if not isinstance(x, str) else x, device)
        vendor, product, serial = device
        result.append((vendor, product, serial))
    return result

# ----------------------------------------------------------------------------
# SET_RELAY()
#
# Set specified relay to chosen state
# ----------------------------------------------------------------------------

def set_relay(cmdarg, relay):

    if cmdarg.verbose:
        print("Device:\t\t", cmdarg.device)
        print("Send command:\tRelay " , cmdarg.relay , " (0x" , relay.address[cmdarg.relay] , ") to " , cmdarg.command.upper())

    try:
        with BitBangDevice(cmdarg.device) as bb:

            # Action towards specific relay
            if cmdarg.relay.isdigit():

                if int(cmdarg.relay) >= 1 and int(cmdarg.relay) <= 8:

                    # Turn relay ON
                    if cmdarg.command == "on":
                        if cmdarg.verbose:
                            print("Relay " , str(cmdarg.relay) , " to ON")
                        bb.port |= int(relay.address[cmdarg.relay], 16)

                    # Turn relay OFF
                    elif cmdarg.command == "off":
                        if cmdarg.verbose:
                            print("Relay "  , str(cmdarg.relay) , " to OFF")
                        bb.port &= ~int(relay.address[cmdarg.relay], 16)

                    # Print relay status
                    elif cmdarg.command == "state":
                        state = get_relay_state( bb.port, cmdarg.relay )
                        if state == 0:
                            if cmdarg.verbose:
                                print("Relay " , cmdarg.relay , " state:\tOFF (" , str(state) , ")")
                            else:
                                print("OFF")
                        else:
                            if cmdarg.verbose:
                                print("Relay " , cmdarg.relay , " state:\tON (" , str(state) , ")")
                            else:
                                print("ON")

            # Action towards all relays
            elif cmdarg.relay == "all":

                if cmdarg.command == "on":
                    if cmdarg.verbose:
                        print("Relay " , str(cmdarg.relay) , " to ON")
                    bb.port |= int(relay.address[cmdarg.relay], 16)

                elif cmdarg.command == "off":
                    if cmdarg.verbose:
                        print("Relay "  , str(cmdarg.relay) , " to OFF")
                    bb.port &= ~int(relay.address[cmdarg.relay], 16)

                elif cmdarg.command == "state":
                    for i in range(1,8):
                        state = get_relay_state( bb.port, str(i) )
                        if state == 0:
                            if cmdarg.verbose:
                                print("Relay " , str(i) , " state:\tOFF (" , str(state) , ")")
                            else:
                                print("OFF")
                        else:
                            if cmdarg.verbose:
                                print("Relay " , str(i) , " state:\tON (" , str(state) , ")")
                            else:
                                print("ON")

                else:
                    print("Error: Unknown command")

            else:
                print("Error: Unknown relay number")
                sys.exit(1)

    except Exception as err:
        print("Error: " , str(err))
        sys.exit(1)

def check():

    # Check python version
    if sys.hexversion < 0x03040000:
        print("Error: Your Python need to be 3.4 or newer")
        sys.exit(1)

    #Check availability on library, this check is also done in pylibftdi
    ftdi_lib = find_library('libftdi1')
    if ftdi_lib is None:
       print("Error: libftdi library not found")
       sys.exit(1)

if __name__ == '__main__':

    # Init objects
    cmdarg = cmdarg_data()
    relay = relay_data()
    app = app_data()

    # Do system check
    check()

    parser = OptionParser()
    parser.add_option("-d", "--device", action="store", type="string", dest="device", help="The device serial, example A6VV5PHY")
    parser.add_option("-l", "--list", action="store_true", dest="list", default=False, help="List all devices")
    parser.add_option("-r", "--relay", action="store", type="string", dest="relay", help="Relay to command by number: 1...8 or all")
    parser.add_option("-c", "--command", action="store", type="string", dest="command", help="State: on, off, state")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Verbose, print all info on screen")

    (options, args) = parser.parse_args()

    if options.verbose:
        cmdarg.verbose = options.verbose
        print(app.name , " " , app.version)
    else:
        cmdarg.verbose = False

    if options.list:
        list_devices()
        sys.exit(0)

    if options.relay or options.command:
        if not options.device:
            print("Error: Device missing")

    if options.device:
        if not options.relay:
            print("Error: Need to state which relay")
            sys.exit(1)
        if not options.command:
            print("Error: Need to specify which relay state")
            sys.exit(1)

        cmdarg.device = options.device
        cmdarg.relay = options.relay.lower()
        cmdarg.command = options.command.lower()

        set_relay()
        sys.exit(0)





