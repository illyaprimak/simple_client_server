import socket
import threading
import sys
from struct import *

#Wait for incoming data from server
#.decode is used to turn the message in bytes to a string
def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(32)
            print(str(data.decode("utf-8")))
        except:
            print("You have been disconnected from the server")
            signal = False
            break

def ReceiveDownload(socket):
    #gets header
    data = socket.recv(8)
    if data != 'ABORT':
        fileb = unpack("<I",data[:4])[0]
        filenamebytes = unpack("<I",data[4:])[0]
        data = socket.recv(filenamebytes)
        filename = data
        curb = 0
        print('Getting '+filename+"...")
        writeto = open('./footage/'+filename,'wb')
        while curb < fileb:
            sys.stdout.flush()
            data = socket.recv(1024)
            writeto.write(data)
            curb += len(data)
            print('\r' + str(curb) + "/" + str(fileb))
        writeto.close()
        print('Download of '+filename+' successful.')
    else:
        print ('Download failed.')

def senddata(filename,socket):
    try:
        filehandle = open(filename,'rb')
    except IOError:
        socket.sendall('ABORT')
        print('File ' +filename+ ' not found; not sending...')
    else:
        #writes 8 byte header consisting of:
        #length of file in kb (4b)
        #length of filename (4b)
        numbytes = pack("<I",math.ceil(os.stat(filename).st_size))
        #amount of KB (1024) to receive, written to 4-byte integer
        filenamebytes = pack("<I",len(filename))
        print('Sending '+filename+'...')
        socket.sendall(numbytes + filenamebytes)
        data = filename
        socket.sendall(data)
        while True:
            data = filehandle.read(1024)
            socket.sendall(data)
            if not data:
                break
        filehandle.close()
        print('Send complete.')

#Get host and port
host = input("Host: ")
port = int(input("Port: "))

#Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

#Create new thread to wait for data
receiveThread = threading.Thread(target = receive, args = (sock, True))
receiveThread.start()

#Send data to server
#str.encode is used to turn the string message into bytes so it can be sent across the network
while True:
    message = input()
    sock.sendall(str.encode(message))
    waiting = sock.recv(1024)
    if waiting == "Type name of file":
        message = input()
        sock.sendall(str.encode(message))
        ReceiveDownload(sock)
    if waiting == "Waiting for file":
        message = input()
        senddata(message, sock)