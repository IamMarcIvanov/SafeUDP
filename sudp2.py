import math
import socket
import hashlib
import threading
import time
import socketserver


class Packet:
    def __init__(self, data='', seqNum=0, ack=False, rst=False):

        self.data = data
        self.header = {"ack": 1 if ack else 0,
                       "rst": 1 if rst else 0,
                       "chk": 0,
                       "seqNum": seqNum,
                       # 64 bytes in length
                       "checkSum": self.getChecksum(self.data),
                       "packetLength": len(self.data) + 74}  # 6 bytes
        self.packet = ''

    def makePacket(self):
        return "00000" + str(self.header['ack']) + str(self.header['rst']) + str(self.header['chk']) + "~~" + str(self.header['seqNum']) + "~~" + str(self.header['checkSum']) + "~~" + str(self.header['packetLength']) + "~~" + self.data

    def getChecksum(self, data):
        return hashlib.sha256(str(data).encode()).hexdigest()


class client:

    def __init__(self, serverIP, serverPort):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = serverIP
        self.port = serverPort
        self.allPackets = None
        self.missingPackets = set()
        self.maxx = 0
        self.udpSocket.setblocking(0)

    def makePacketList(self, filename):
        packetList = list()

        seq = 0
        chunkSize = 1024
        fo = open(filename, "r")
        parts = list()

        while(True):
            part = fo.read(chunkSize)
            if not part:
                break
            else:
                parts.append(part)
                print("Data length is", len(part))

        for part in parts:
            tempPkt = Packet(data=part, seqNum=seq).makePacket()
            packetList.append(tempPkt)
            print("Packet length is", len(tempPkt))
            self.missingPackets.add(seq)
            seq += 1
        self.maxx = seq
        # print("maxx   ", int(self.maxx))
        # insert reset packet to end the connection
        packetList.append(Packet("", seq, rst=True).makePacket())
        self.allPackets = list(packetList)
        self.allPackets.pop()
        return packetList

    def send(self):
        # IMPLEMENT SELECTIVE REPEAT HERE!!!
        filename = str(input('Enter the name of file you want to send:'))
        packets = self.makePacketList(filename)
        # print(packets)
        for packet in packets:
            self.udpSocket.sendto(bytes(packet, 'utf-8'), (self.ip, self.port))
            print('packet sent')
        # the sending object shd be of bytes format.
        print("Total Msg sent first time")
        # setting timeout to prevent waiting forever
        self.udpSocket.settimeout(0.5)
        while(True):
            reply = None

            try:
                reply = self.udpSocket.recvfrom(4096)
            except Exception as e:
                print("Timeout Occured! Checking possible actions..")
                if(len(self.missingPackets) == 0):
                    print("Complete Transfer Successfull.. Bye Bye server..")
                    self.udpSocket.sendto(
                        Packet("", -1, rst=True).makePacket().encode(), (self.ip, self.port))
                    break
                else:
                    print("missing packkks")
                    print(self.missingPackets)
                    for i in self.missingPackets:
                        self.udpSocket.sendto(
                            bytes(self.allPackets[i], 'utf-8'), (self.ip, self.port))
                    self.udpSocket.sendto(
                        Packet("", self.maxx, rst=True).makePacket().encode(), (self.ip, self.port))
                    # continue

            # We have received in specified time. Check for the type of msg and do appropriate action.
            if reply is not None:
                message = reply[0]
                address = reply[1]
                message = message.decode().split("~~")
            # message[0] = flagbits, [0][6] = rst, [0][5] = ack, [0][7] = chk
            # message[1] = seqnum
            # message[2] = checkSum
            # message[3] = packetLength
            # message[4] = data

            # Check for rst packet
                if(message[0][6] == "1" and message[1] == "-1" and message[0][5] != "1"):
                    # self.udpSocket.sendto(str("reset Pcket received..! Now F off").encode(), address)
                    print("Complete transfer successfull")
                    break
            # check for ack packet
                elif(message[0][5] == "1" and message[1] != "-1" and message[0][6] != "1"):
                    print("Missing packets are", self.missingPackets)
                    self.missingPackets.remove(int(message[1]))
                    print("received ack for packet", message[1])
            # Check for missing packets list
                elif(message[1] == "-1" and message[0][5] == "1" and message[0][6] == "1"):
                    # We have received the list of dropped packets in data.
                    print("Dropped packets are:", message[4].split(';')[:-1])
                    for i in message[4].split(';')[:-1]:
                        self.missingPackets.add(int(i))
                        print("Resending packet", i)
                        self.udpSocket.sendto(
                            bytes(self.allPackets[int(i)], 'utf-8'), (self.ip, self.port))
                    self.udpSocket.sendto(
                        Packet("", self.maxx, rst=True).makePacket().encode(), address)

        print("Closing connection to server.")
        self.udpSocket.close()


class server:
    localIP = "127.0.0.1"
    localPort = 20001

    def __init__(self):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind((self.localIP, self.localPort))
        self.udpSocket.setblocking(0)
        print("Server is up!")

    def listen(self):
        recvBuffer = list()
        recvSeqBuffer = list()  # Stores the received seqnum's in order
        # HANDLE SENDING ACK'S HERE! AND STORING RECEIVED DATA INTO BUFFERS.

        self.udpSocket.settimeout(30)
        all_recv = False
        while(True):
            bytesAddressPair = None

            try:
                bytesAddressPair = self.udpSocket.recvfrom(4096)
            except Exception as e:
                if all_recv:
                    print("Closing connection!!")
                    break
                # continue

            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            message = message.decode().split("~~")
            # message[0] = flagbits, [0][6] = rst, [0][5] = ack, [0][7] = chk
            # message[1] = seqnum
            # message[2] = checkSum
            # message[3] = packetLength
            # message[4] = data
            if(message[0][6] == "1"):
                if message[1] == "-1":
                    break
                print("Client sent rst packet. Checking for missing packets...")
                # we have received a rst packet ==> client is done sending.
                # check if we have received every packet.

                # HANDLE THE CASE IN CLIENT WHERE THIS RST PACKAGE GETS DROPPED
                missingSeqNum = list()
                Max = message[1]
                # print("MMMMAAAxxx ", int(Max))
                for i in range(int(Max)):
                    if i not in recvSeqBuffer:
                        missingSeqNum.append(i)

                if len(missingSeqNum) == 0:
                    # we have received every packet. send an rst message to client to stop
                    # further sending msgs.
                    print(
                        "No packets dropped.. sending rst packet to client!!! yayy.. ;)")
                    all_recv = True
                    rstPacket = Packet("", -1, rst=True).makePacket().encode()
                    #self.udpSocket.sendto(rstPacket, address)
                    # break
                else:
                    # send the missing packets list as data to resend again.
                    # if seq = -1, ack and rst are true then the data in the msg
                    # contains the indices of missing packet list.
                    drpdData = ""
                    for i in missingSeqNum:
                        drpdData += str(i) + ';'
                        print("Missing packet", i)
                    drpdPackets = Packet(
                        drpdData, -1, ack=True, rst=True).makePacket().encode()
                    #print('Data', drpdPackets)
                    self.udpSocket.sendto(drpdPackets, address)
                    print('Server sent request for missing packets\n')
            else:
                if hashlib.sha256(message[4].encode()).hexdigest() == message[2]:
                    print("Received packet", message[1])
                    # handles duplicates
                    if(int(message[1]) not in recvSeqBuffer):
                        recvBuffer.append(message[4])
                        recvSeqBuffer.append(int(message[1]))
                    ackPacket = Packet(
                        "", message[1], ack=True).makePacket().encode()
                    self.udpSocket.sendto(ackPacket, address)
                    print("sent ack for", message[1])
                else:
                    print("Packet", message[1],
                          "found corrupted.Dropped it..!!")

        # ASSUMING SUCCESSFULL RECEIVE OF ALL DATA. REORDER THEM AND WRITE TO FILE.
        print("Closing connection.. bye bye client")
        self.udpSocket.close()

        print("Writing to received.txt....")
        maxi = max(recvSeqBuffer)+1
        # SHD HANDLE MULTIPLE TYPES OF FILES
        f = open("received.txt", "w")
        for i in range(int(maxi)):
            index = recvSeqBuffer.index(i)
            f.write(recvBuffer[index])
        print("Write succesfull... goodbye...")
