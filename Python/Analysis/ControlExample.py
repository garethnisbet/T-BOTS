import pygame, sys, pygame.mixer
from pygame.locals import *
import socket
from time import sleep
bd_addr = '98:D3:32:21:40:D6'
port = 1
sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
sock.connect((bd_addr,port))
def send(sendstr):
    try:
        sock.send(sendstr.encode(encoding='utf-8'))
    except:
        sock.close()
        sys.exit()

for jx in range(150,280,10)+[200]:
        jy = jx
        print('x '+str(jx)+' y '+str(jy))
        sendstring = chr(0X02)+str(jx)+str(jy)+chr(0X03)
        send(sendstring)
        sleep(2)

sock.close()
sys.exit()
