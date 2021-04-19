import math
import socket
import hashlib
import threading
import time
import socketserver
import base64


BUFF_SIZE = 4096
CHUNK_SIZE = 512
class Packet:
    def __init__(self, data='', seqNum=0, ack=False, rst=False):

        self.data = data # base64
        self.header = {"ack": 1 if ack else 0,
                       "rst": 1 if rst else 0,
                       "chk": 0,
                       "seqNum": seqNum,
                       "checkSum": self.getChecksum(self.data), # 64 bytes in length
                       "packetLength": len(self.data) + 74} # 6 bytes

    def makePacket(self):
        pkt_str = "00000" + str(self.header['ack']) + str(self.header['rst']) + str(self.header['chk']) + "~~" + str(self.header['seqNum']) + "~~" + str(self.header['checkSum']) + "~~" + str(self.header['packetLength']) + "~~"
        pkt_bstr = bytes(pkt_str, 'utf-8') + base64.decodebytes(self.data)
        return base64.encodebytes(pkt_bstr)
        #return "00000" + str(self.header['ack']) + str(self.header['rst']) + str(self.header['chk']) + "~~" + str(self.header['seqNum']) + "~~" + str(self.header['checkSum']) + "~~" + str(self.header['packetLength']) + "~~" + self.data

    def getChecksum(self, data):
        return hashlib.sha256(base64.decodebytes(data)).hexdigest()

class client:

    def __init__(self,serverIP,serverPort):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = serverIP
        self.port = serverPort
        self.allPackets = None
        self.missingPackets = set()

    def makePacketList(self,filename):
        packetList = list()

        seq = 0
        fo = open(filename,"rb").read()
        parts = []

        i = 0
        while(True):
            part = base64.encodebytes(fo[CHUNK_SIZE * i : CHUNK_SIZE * (i + 1)])
            if not part:
                break
            else:
                parts.append(part)
                print("Data length is",len(part))
            i += 1

        for part in parts:
            print(type(part))
            tempPkt = Packet(part, seq).makePacket()
            packetList.append(tempPkt)
            print("Packet length is", len(tempPkt))
            self.missingPackets.add(seq)
            seq += 1

        #insert reset packet to end the connection
        packetList.append(Packet(base64.encodebytes(bytes('', 'utf-8')), -1, rst=True).makePacket())
        self.allPackets = packetList
        self.allPackets.pop()
        return packetList

    def send(self):
        # IMPLEMENT SELECTIVE REPEAT HERE!!!
        filename = str(input('Enter the name of file you want to send:'))
        packets = self.makePacketList(filename)
        # print(packets)
        for packet in packets:
            self.udpSocket.sendto(packet, (self.ip,self.port))
            print('packet sent')
        # the sending object shd be of bytes format.
        print("Total Msg sent first time")
        # setting timeout to prevent waiting forever
        self.udpSocket.settimeout(3)
        while(True):
            reply = None
            #try:
            #    self.udpSocket.send("1")
            #except:
            #    print('Server found to be closed')
            #    break
            
            try:
                message, address, = self.udpSocket.recvfrom(BUFF_SIZE)
            except Exception as e:
                print("Timeout Occured! Checking possible actions..")
                if(len(self.missingPackets) == 0):
                    print("Complete Transfer Successfull.. Bye Bye server..")
                    break
                else:
                    print('Missing packets are:', self.missingPackets)
                    for i in self.missingPackets:
                        self.udpSocket.sendto(self.allPackets[i], (self.ip,self.port))
                    self.udpSocket.sendto(Packet(base64.encodebytes(bytes('', 'utf-8')),-1,rst=True).makePacket(), (self.ip,self.port))
                    continue

            # We have received in specified time. Check for the type of msg and do appropriate action.
            message = base64.decodebytes(message).split(b"~~", 4)
            # message[0] = flagbits, [0][6] = rst, [0][5] = ack, [0][7] = chk
            # message[1] = seqnum
            # message[2] = checkSum
            # message[3] = packetLength
            # message[4] = data
            message[0].decode('ascii')
            message[1].decode('ascii')
            message[2].decode('ascii')
            message[3].decode('ascii')

            # Check for rst packet
            if(message[0][6] == "1" and message[1] == "-1" and message[0][5] != "1"):
                # self.udpSocket.sendto(str("reset Pcket received..! Now F off").encode(), address)
                print("Complete transfer successfull")
                break
            # check for ack packet
            elif(message[0][5] == "1" and message[1] != "-1" and message[0][6] != "1"):
                self.missingPackets.remove(int(message[1]))
                print("received ack for packet", message[1])
            # Check for missing packets list
            elif(message[1] == "-1" and message[0][5] == "1" and message[0][6] == "1"):
                # We have received the list of dropped packets in data.
                #print("Dropped packets are:",message[4].split(';')[:-1])
                for i in message[4].split(b';')[:-1]:
                    print("Resending packet", i)
                    self.missingPackets.add(int(i))
                    self.udpSocket.sendto(self.allPackets[int(i)], (self.ip,self.port))
                self.udpSocket.sendto(Packet(base64.encodebytes(bytes('', 'utf-8')), -1, rst=True).makePacket(), address)

        print("Closing connection to server.")
        self.udpSocket.close()

class server:
    localIP = "127.0.0.1"
    localPort = 20001
    def __init__(self):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind((self.localIP,self.localPort))
        print("Server is up!")

    def listen(self):
        recvBuffer = []
        recvSeqBuffer = [] #Stores the received seqnum's in order
        # HANDLE SENDING ACK'S HERE! AND STORING RECEIVED DATA INTO BUFFERS.

        self.udpSocket.settimeout(3)
        while(True):
            bytesAddressPair = None

            try:
                message, address, = self.udpSocket.recvfrom(BUFF_SIZE)
            except Exception as e:
                continue

            message = base64.decodebytes(message).split(b"~~", 4)
            # message[0] = flagbits, [0][6] = rst, [0][5] = ack, [0][7] = chk
            # message[1] = seqnum
            # message[2] = checkSum
            # message[3] = packetLength
            # message[4] = data
            message[0].decode('ascii')
            message[1].decode('ascii')
            message[2].decode('ascii')
            message[3].decode('ascii')
            #if len(message[4]) < 10:
            #    continue
            if(message[0][6] == "1"):
                print("Client sent rst packet. Checking for missing packets...")
                # we have received a rst packet ==> client is done sending.
                # check if we have received every packet.

                #### HANDLE THE CASE IN CLIENT WHERE THIS RST PACKAGE GETS DROPPED
                missingSeqNum = []
                Max = max(recvSeqBuffer)+1
                for i in range(Max):
                    if i not in recvSeqBuffer:
                        missingSeqNum.append(i)

                if len(missingSeqNum) == 0:
                    # we have received every packet. send an rst message to client to stop
                    # further sending msgs.
                    print("No packets dropped.. sending rst packet to client!!! yayy.. ;)")
                    rstPacket = Packet(base64.encodebytes(bytes('', 'utf-8')), -1, rst=True).makePacket()
                    self.udpSocket.sendto(rstPacket, address)
                    break
                else:
                    # send the missing packets list as data to resend again.
                    # if seq = -1, ack and rst are true then the data in the msg
                    # contains the indices of missing packet list.
                    drpdData = ""
                    for i in missingSeqNum:
                        drpdData += str(i) + ';'
                        print("Missing packet",i)
                    drpdPackets = Packet(drpdData, -1, ack=True, rst=True).makePacket()
                    #print('Data', drpdPackets)
                    self.udpSocket.sendto(drpdPackets, address)
                    print('Server sent request for missing packets\n')
            else:
                eq_add = b'=' * (len(message[4]) % 4 + 1)
                print(len(message[4]))
                if hashlib.sha256(base64.decodebytes(message[4] + eq_add)).hexdigest() == message[2]:
                    print("Received packet", message[1])
                    # handles duplicates
                    if(int(message[1]) not in recvSeqBuffer):
                        recvBuffer.append(message[4])
                        recvSeqBuffer.append(int(message[1]))
                    ackPacket = Packet(base64.encodebytes(bytes('', 'utf-8')), message[1], ack=True).makePacket()
                    print('sending ack', message[1])
                    self.udpSocket.sendto(ackPacket, address)

        # ASSUMING SUCCESSFULL RECEIVE OF ALL DATA. REORDER THEM AND WRITE TO FILE.
        print("Closing connection.. bye bye client")
        self.udpSocket.close()

        print("Writing to received.txt....")
        maxi = max(recvSeqBuffer) + 1
        #### SHD HANDLE MULTIPLE TYPES OF FILES
        f = open("received.txt", "wb")
        for i in range(maxi):
            index = recvSeqBuffer.index(i)
            f.write(base64.decodebytes(recvBuffer[index]))
        print("Write succesfull... goodbye...")