import sqlite3
import requests
import json

class ogndb:
        def __init__(self):
                self.conn = self.initdb()

        def loadOgndb(self):
                print('Loading OGN device DB')
                ogndb = requests.get('https://ddb.glidernet.org/download', stream=True)
                for line in ogndb.iter_lines():

                    # filter out keep-alive new lines
                    if line:
                        decoded_line = line.decode('utf-8')
                        record = decoded_line.split(',')
                        record = [f.strip("'") for f in record]
                        self.conn.execute('INSERT INTO t_ogndb VALUES {}'.format(entry=",".join(["?"]*len(record))), record)
                        
        def countdb(self):
                c = self.conn.execute('''SELECT COUNT(*) from t_ogndb''')
                return c.fetchone()
        
        def get_by_device(self,device):
                t = (device,)
                c = self.conn.execute('SELECT * FROM t_ogndb WHERE DEVICE_ID=?', t)
                return c.fetchone()
        
        def initdb(self):
                conn = sqlite3.connect(':memory:')#(self.output_file)        
                # Create table for ogn db
                conn.execute('''CREATE TABLE t_ogndb
                             (DEVICE_TYPE text,DEVICE_ID text,AIRCRAFT_MODEL text,REGISTRATION text,CN text,TRACKED text,IDENTIFIED text)''')
                return conn

if __name__=='__main__':
        c = ogndb()
        c.loadOgndb()
        print(c.countdb())
        print(c.get_by_device('DDFB54'))
