import logging
from pathlib import Path
import time
from os import listdir
from os.path import isfile, join
import shutil
BUFFERSIZE = 1024
logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-2s) %(message)s',)


def ls(ruta = 'prueba/.'):
    return [arch for arch in listdir(ruta) if isfile(join(ruta, arch))]

class protocoloTFP(object):
    def __init__(self,p='null',u='null'):
        self.pw=p
        self.user=u

    def cliente_login(self,TCPClientSocket,p,u):
        logging.debug("Enviando comando : Login\n")
        TCPClientSocket.send(str("Login").encode('utf-8'))
        Mensaje = str(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
        if str(Mensaje)=='ok':
            p = input("\nIngrese usuario: ")
            TCPClientSocket.send(str("USER," + p).encode('utf-8'))
            Mensaje = str(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
            logging.debug(Mensaje)
            c = input("\nIngrese Contrasena: ")
            TCPClientSocket.send(str("PASS," + c).encode('utf-8'))
            Mensaje = str(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
            if int(Mensaje) == 230:
                logging.debug('Server ' + Mensaje + " : Usuario conectado")
            else:
                logging.debug('Server ' + Mensaje + " : Usuario o contraseña incorrectas")
                self.sCLOSE(TCPClientSocket)

    def cliente_Connect(self,TCPClientSocket,HOST,PORT):
        TCPClientSocket.connect((HOST, PORT))
        logging.debug("Enviando comando : Conect")
        TCPClientSocket.send(str('CONECT').encode('utf-8'))
        Mensaje= str(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
        logging.debug(Mensaje)

    def cliente_DIR(self, TCPClientSocket):
        logging.debug("Enviando comando DIR")
        TCPClientSocket.send(str('dir').encode('utf-8'))
        mensaje = str(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
        logging.debug(mensaje)
        dir = str(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
        time.sleep(1)
        print(dir)

    def cliente_SET(self, TCPClientSocket):
        com = input("\n\nArchivos disponibles:")
        logging.debug("Enviando comando SET")
        TCPClientSocket.send(str('SET,'+ com).encode('utf-8'))
        mensaje = str(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
        logging.debug("Server :"+mensaje)

        if int(mensaje)==213:
            self.recibir_Archivo(TCPClientSocket)

        else:
            self.sCLOSE(TCPClientSocket)
    
    def cliente_CLOSE(self, TCPClientSocket):
        logging.debug("Enviando comando CLOSE")
        TCPClientSocket.send(str('CLOSE').encode('utf-8'))
        mensaje = str(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
        logging.debug(mensaje)
    
    def server_Login(self, conn):
        Mensaje = str(conn.recv(BUFFERSIZE).decode('utf-8'))
        conn.send(str('ok').encode('utf-8'))
        logging.debug(Mensaje)
        u = str(conn.recv(BUFFERSIZE).decode('utf-8'))
        coman, U = u.split(',')
        logging.debug('Recibiendo: '+coman+' respuesta: 231')
        conn.send(str('Server  231: necesita contraseña').encode('utf-8'))
        p = str(conn.recv(BUFFERSIZE).decode('utf-8'))
        coman, P = p.split(',')
        if str(U)==self.user and str(P)==self.pw:
              logging.debug('Recibiendo: ' + coman + ' respuesta: 230')
              conn.send(str('230').encode('utf-8'))
        else:
              logging.debug('Recibiendo: ' + coman + ' respuesta: 530')
              conn.send(str('530').encode('utf-8'))
              self.sCLOSE(conn)

    def server_DIR(self, conn):
        Mensaje = str(conn.recv(BUFFERSIZE).decode('utf-8'))
        logging.debug('Recibiendo: ' +Mensaje+",Respuesta: 200")
        conn.send(str('Server: 200').encode('utf-8'))
        dir=str(ls())
        conn.send(str(dir).encode('utf-8'))

    def server_SET(self, conn):
        Mensaje = str(conn.recv(BUFFERSIZE).decode('utf-8'))
        com,img =Mensaje.split(',')
        logging.debug('Recibiendo: '+com+",Respuesta: 200")
        fileName = "prueba/" + str(img)
        fileObj = Path(fileName)
        if fileObj.is_file():
            logging.debug('Respuesta: 213, archivo existente')
            conn.send(str('213').encode('utf-8'))
            self.enviar_Archivo(conn,img)
        else:
            logging.debug('Respuesta: 501,archivo no existente')
            conn.send(str('501').encode('utf-8'))

    def server_CLOSE(self, conn):
        Mensaje = str(conn.recv(BUFFERSIZE).decode('utf-8'))
        logging.debug('Recibiendo: ' +Mensaje+",Respuesta: 221")
        conn.send(str('Server: 221').encode('utf-8'))

    def server_Connect(self,TCPClientSocket):
        conn, addr = TCPClientSocket.accept()
        print("Conectando")
        Mensaje = str(conn.recv(BUFFERSIZE).decode('utf-8'))
        conn.send(str('Server: 200').encode('utf-8'))
        logging.debug('Recibiendo: ' + Mensaje + ",Respuesta: 200")
        return conn


    def enviar_Archivo(self, conn,file):
        o='prueba/'+ file
        d='prueba2/'+ file #IMGC
        shutil.copy(o,d)
        time.sleep(2)
        conn.send(str('250').encode('utf-8'))
        logging.debug("Archivo enviado, Respuesta 250")

    def recibir_Archivo(self, TCPClientSocket):
        while True:
            recibido = int(TCPClientSocket.recv(BUFFERSIZE).decode('utf-8'))
            if int(recibido)==250:
                logging.debug("Server "+str(recibido)+" : Archivo descargado")
                break