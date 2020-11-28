#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ogn_ngc.py
#  
#  Copyright 2020  <pi@nirpi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
from ogn.client import TelnetClient
from ogn.parser.telnet_parser import parse
from terminaltables import AsciiTable
import json 
import sys

class beacon_server:
    def __init__(self):
        self.gliders = {}
        self.th = ['address','frequency','distance','ground_speed','altitude']
        
    def process_beacon(self,raw_message):
        beacon = parse(raw_message)
        td = [self.th]
        if beacon:
            self.gliders[beacon['address']] = beacon
            for g in self.gliders.items():
                td.append([g[0], g[1]['frequency'], g[1]['distance'], g[1]['ground_speed'],g[1]['altitude']])
            
            table = AsciiTable(td)
            table.title = 'Flight board'
            print(table.table)
                
            with open ('teiman_log.dict', mode='a') as f:
                f.write(str(beacon) )           


def main(args):
    client = TelnetClient()
    client.connect()
    process_beacon = beacon_server()
    try:
        client.run(callback=process_beacon.process_beacon)
    except KeyboardInterrupt:
        print('\nStop ogn gateway')
        client.disconnect()
            
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
