#!/usr/bin/python3
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
import os
import sys
import curses
import requests
import sqlite3
import csv
import json

from ogn.client import TelnetClient
from ogn.parser.telnet_parser import parse
from terminaltables import AsciiTable
from datetime import date
from dotenv import load_dotenv

class beacon_server:
    def __init__(self, args):
        # import environment variables from .env file
        load_dotenv()
        self.onsign_appid = os.getenv('onsign_appid')
        if self.onsign_appid is None:
            print('No messaging service detected ')
            
        else:
            print ('Onsign messaging service detected')
            self.onsign_apikey = os.getenv('onsign_apikey')
        
        # import commandline parameters
        self.args = args
        
        self.gliders = {}
        self.th = ['address','frequency','distance','ground_speed','altitude']
        
        # init the logfile envvironment
        nowdate = date.today()
        self.output_dir = 'logfiles'
        self.output_file = '{}/LLBS_{}.log'.format(self.output_dir,nowdate.strftime('%a_%d%m%y'))  
        
        #init the database
        self.conn = self.initdb()

        self.loadOgndb()
        self.sendMessage('OGN receiver in LLBS is online')
        
        if 'service'  in args:
            self.screen = None
        else:
            self.screen = curses.initscr()

        
    def terminate(self):
        if not self.screen is None:
            curses.endwin()
        self.conn.close()
        
    def initdb(self):
        conn = sqlite3.connect(':memory:')#(self.output_file)        
        # Create table for ogn db
        conn.execute('''CREATE TABLE t_ogndb
                     (DEVICE_TYPE text,DEVICE_ID text,AIRCRAFT_MODEL text,REGISTRATION text,CN text,TRACKED text,IDENTIFIED text)''')
        
        # Create table for parsed APRS
        conn.execute('''CREATE TABLE t_aprs 
                        (address text, frequency text, distance text, ground_speed text, altitude text) ''')
        return conn
    
    def loadOgndb(self):
        print('Loading OGN device DB')
        ogndb = requests.get('https://ddb.glidernet.org/download', stream=True)
        for line in ogndb.iter_lines():

            # filter out keep-alive new lines
            if line:
                decoded_line = line.decode('utf-8')
                record = decoded_line.split(',')
                record = [f.strip("'") for f in record]

                self.conn.execute('INSERT INTO t_ogndb VALUES (?,?,?,?,?,?,?)', record)
                #rint(json.loads(decoded_line))

                    
    def disp(self, td):
        if not self.screen is None:
            table = AsciiTable(td)
            table.title = 'Flight board'
            self.screen.addstr(0, 0, table.table)
            self.screen.refresh()
            #curses.napms(10)
            
    def sendMessage(self, text):
        if 'service' in self.args:
            header = {"Content-Type": "application/json; charset=utf-8",
                      "Authorization": "Basic {}".format(self.onsign_apikey)}

            payload = {"app_id": self.onsign_appid,
                       #"included_segments": ["test"],
                       "include_external_user_ids": ["52","264","164"],
                       "heading": {"en": "OGN Receiver LLBS"},
                       "contents": {"en": text}}
            req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
            print('push message sent:{} result:{} {}'.format(text,req.status_code, req.reason))        
        
    def update_db (self,beacon):
        columns = ', '.join(beacon.keys())
        placeholders = ', '.join('?' * len(beacon))
        sql = 'INSERT INTO Media ({}) VALUES ({})'.format(columns, placeholders)
        self.conn.execute(sql, values.values())

        
    def process_beacon(self,raw_message):
        beacon = parse(raw_message)
        td = [self.th]
        if beacon:
            # fetch the device info from ogndb
            t = (beacon['address'],)
            c = self.conn.execute('SELECT * FROM t_ogndb WHERE DEVICE_ID=?', t)
            ogn_db_rec = c.fetchone()
            
            # update registration if in db else update device-id
            if ogn_db_rec is None:
                registration = beacon['address']
            else:
                registration = ogn_db_rec[3] # registration
            
            self.gliders[registration] = beacon
            for g in self.gliders.items():
                td.append([g[0], g[1]['frequency'], g[1]['distance'], g[1]['ground_speed'],g[1]['altitude']])
            
            if not 'no-logfile' in self.args:    
                with open (self.output_file, mode='a') as f:
                    f.write(str(beacon) ) 
        self.disp(td)



def main(args):
    client = TelnetClient()
    client.connect()
    process_beacon = beacon_server(args)
    try:
        client.run(callback=process_beacon.process_beacon)
    except KeyboardInterrupt:
        print('\nStop ogn gateway')
        client.disconnect()
        process_beacon.terminate()
            
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
