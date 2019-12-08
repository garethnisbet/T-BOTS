#!/usr/bin/python
from time import sleep, time

class bt_connect(object):
    def __init__(self,bt_addr,port,lib,baudrate=38400):
        self.bt_addr = bt_addr
        self.port = port
        self.lib = lib
        self.baudrate = baudrate
    def connect(self,con):
        if con == 1:
            try:
                if self.lib == 'PyBluez':
                    try:
                        import bluetooth as bt
                    except:
                        print('Cannot import PyBluez\nIt might not be installed, try pip install pybluez')
                    print('connecting to '+self.bt_addr)
                    self.sock = bt.BluetoothSocket( bt.RFCOMM )
                    self.sock.connect((self.bt_addr,self.port))
                    self.sock.settimeout(5)
                    print('connected to '+self.bt_addr)
                    
                elif self.lib == 'Socket':
                    try:
                        import socket
                    except:
                        print('Cannot import Socket\nTry using PyBluez or PySerial')
                    print('connecting to '+self.bt_addr)
                    self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                    self.sock.connect((self.bt_addr,self.port))
                    print('connected to '+self.bt_addr)
                    
                elif self.lib == 'PySerial':
                    try:
                        import serial
                    except:
                        print('Cannot import serial\nTry using Socket or PyBluez')
                    print('connecting to '+self.port+' with a baud rate of '+ str(self.baudrate))
                    self.sock = serial.Serial(self.port, self.baudrate)
                    print('connected to '+self.port+' with a baud rate of '+ str(self.baudrate))               
                
                
                return self.sock.getpeername()
            except:
                print('Connection Failed')
                
        else:
            try:
                print('Closing connection to '+self.bt_addr)
                self.sock.close()
                return 'Disconnected'
            except:
                return 'Not connected'
                
    def connected(self):
        try:
            self.sock.getpeername()
            status = 1
        except:
            status = 0
        return status

    def send_data(self,sendstr,sendtwice):
        try:
            if sendstr == '200200Z':
                if sendtwice <= 2:
                    builtstr = chr(0X02)+sendstr+chr(0X03)
                    if self.lib == 'PySerial':
                        self.sock.write(builtstr.encode(encoding='utf-8'))
                    else:
                        self.sock.send(builtstr.encode(encoding='utf-8'))
                    sendtwice += 1
                  
            else:
                builtstr = chr(0X02)+sendstr+chr(0X03)
                self.sock.send(builtstr.encode(encoding='utf-8'))
                sendtwice = 0

        except:
            print('Error sending data...')
        return sendtwice

    def get_data(self,oldvalues = [0,0,0,0]):
        if self.lib == 'PySerial':
            try:
                data = self.sock.read(32).decode(encoding='utf-8')
                data = data.split('\x02')
                ministring = data[0]
                splitstr = ministring.split(',')
            except:
                splitstr = []
        else:
            try:
                data = self.sock.recv(32).decode(encoding='utf-8')
                data = data.split('\x02')
                ministring = data[0]
                splitstr = ministring.split(',')
            except:
                splitstr = []
        
        if len(splitstr) == 4:
            oldkps, oldkp, oldtrim, oldgyro = splitstr[0], splitstr[1], splitstr[2], splitstr[3]
            oldgyro = oldgyro[:-2]
            oldvalues = [oldkps, oldkp, oldtrim, oldgyro]
            return oldkps, oldkp, oldtrim, float(oldgyro)
        else:
            return oldvalues[0], oldvalues[1],oldvalues[2],oldvalues[3]
            
    def get_name(self):
        try:
            return self.sock.getpeername()
        except:
            return 'Not Connected'

