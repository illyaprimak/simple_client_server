import socket
import threading
import os
import math
from struct import *
# Variables for holding information about connections
connections = []
total_connections = 0
waiting = ""

# Client class, new instance created for each connected client
# Each instance has the socket and address that is associated with items
# Along with an assigned ID and a name chosen by the client
class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal

    def __str__(self):
        return str(self.id) + " " + str(self.address)

    # Attempt to get data from client
    # If unable to, assume client has disconnected and remove him from server data
    # If able to and we get data back, print it in the server and send it back to every
    # client aside from the client that has sent it
    # .decode is used to convert the byte data into a printable string
    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(32)
            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                break
            global waiting
            if waiting == 'send':
                for client in connections:
                    if client.id == self.id:
                        senddata(data.decode("utf-8"),self.socket)
            if waiting == 'receive':
                for client in connections:
                    if client.id == self.id:
                        ReceiveDownload(self.socket)
            if data != "":
                if data == "send":
                    for client in connections:
                        if client.id == self.id:
                            message = "Type name of file"
                            waiting = 'send'
                            client.socket.sendall(str.encode(message))
                if data == "receive":
                    for client in connections:
                        if client.id == self.id:
                            message = "Waiting for file"
                            waiting = 'receive'
                            client.socket.sendall(str.encode(message))
                print(self.socket)
                print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
                for client in connections:
                    if client.id == self.id:
                        client.socket.sendall(data)


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


# Wait for new connections
def newConnections(socket):
    while True:
        sock, address = socket.accept()
        global total_connections
        connections.append(Client(sock, address, total_connections, "Name", True))
        connections[len(connections) - 1].start()
        print("New connection at ID " + str(connections[len(connections) - 1]))
        total_connections += 1


def main():
    # Get host and port
    host = input("Host: ")
    port = int(input("Port: "))

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    # Create new thread to wait for connections
    newConnectionsThread = threading.Thread(target=newConnections, args=(sock,))
    newConnectionsThread.start()


main()