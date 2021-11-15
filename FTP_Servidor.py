import socket
import threading
import logging
import time
from FTP import *

bufferSize = 1024
logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-2s) %(message)s',)


def servirPorSiempre(TCPServerSocket,FTP):
    print("Servidoren espera...")
    try:
        while True:
            Client_conn=FTP.server_Connect(TCPServerSocket)
            thread_read = threading.Thread(name='Server', target=servicio, args=[Client_conn])
            thread_read.start()
    except Exception as e:
        print(e)

def servicio(conn):
     FTP.server_Login(conn)
     FTP.server_DIR(conn)
     FTP.server_SET(conn)
     FTP.server_CLOSE(conn)
 
HOST = '172.16.8.13'
PORT = 21  

threading.current_thread().setName("Server")
FTP=protocoloTFP('password','admin')
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen()
    print("El servidor FTP está disponible y en espera de solicitudes")
    servirPorSiempre(TCPServerSocket,FTP)
