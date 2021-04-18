<<<<<<< Updated upstream
# %%
import math
import socket
import hashlib

MAX_SEG_SIZE = 256
SENDER_WINDOW_SIZE = 50
SERV_PORT = 12345
RECV_PORT = 12346
RECEIVER_WINDOW_SIZE = 50
RECV_BUFF_SIZE = 4096

# !create Timer
# !create method to extract packet from received string
# !create deliver data function
# !implement rst

class Packet: 
    def __init__(self, data='', seqNum=0, ack=False, rst=False):
        """[summary]

        Args:
            data (str, optional): [description]. Defaults to ''.
            seqNum (int, optional): [description]. Defaults to 0.
            ack (bool, optional): [description]. Defaults to False.
            rst (bool, optional): [description]. Defaults to False.
        
        Vars:
            self.data (str): [No fixed size] the data that the user client wants to send. Text string.
            self.header (dict): 
                ack (int): [1 bit] 1 if this is acknowledge packet else 0. 
                rst (int): [1 bit] 1 if this is reset packet else 0.
                chk (int): [1 bit] 1 if checksum is for header and data, else 0 if just for data.
                seqNum (int): [3 bytes] 3 bytes (add zeroes if not len == 3)
                checkSum (hexString): [64 bytes] SHA 256 
                packetLength (str): [6 bytes] (add zeroes if not len == 6)
                    1 byte for flags +
                    3 for sequence number +
                    64 for checksum +
                    6 for packet length = 74 bytes
        """
        
        self.data = data 
        self.header = {"ack": 1 if ack else 0,
                       "rst": 1 if rst else 0,
                       "chk": 0,
                       "seqNum": seqNum, 
                       "checkSum": self.getChecksum(self.data), # 64 bytes in length
                       "packetLength": len(data) + 74} # 6 bytes
        self.packet = ''
        
    def makePacket(self):
        flags = int("00000" + str(self.header['ack']) + str(self.header['rst']) + str(self.header['chk']), 2)
        n_add0_seqNum = 3 - len(str(seqNum))
        n_add0_pkt_len = 6 - len(str(len(data) + 74))
        headerStr = str(flags) + '0' * n_add0 + str(self.header['seqNum']) + str(self.header['checkSum']) + '0' * n_add0_pkt_len + str(self.header['packetLength'])
        return headerStr + data
    
    def getChecksum(self, data):
        return hashlib.sha256(data).hexdigest()


class SUDP:
    def __init__(self, ip):
        self.receiverIP = ip
        self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendSocket.bind((str(self.receiverIP), SERV_PORT))
        self.sendSocket.setblocking(0)
        self.senderNextSeqNum = 0
        self.MSS = MAX_SEG_SIZE
        self.senderBuffer = [0] * self.MSS
        self.senderWindowSize = SENDER_WINDOW_SIZE
        self.senderBase = 0
        # 0 means unsent
        # 1 means sent but ack not received
        # 2 means sent and ack received
        
        self.receiverStatusBuffer = [0] * self.MSS
        self.receiverDataBuffer = [0] * self.MSS
        self.receiverWindowSize = RECEIVER_WINDOW_SIZE
        self.receiverBase = 0
        self.receiverSeqNum = 0
        # 0 means not received
        # 1 means sent ack
    
    def sendPacket(self, data, ip):
        self.sendSocket.sendto(bytes(data.encode('utf-8')), (ip, RECV_PORT))
    
    def setPacket(self, data):
        pktReceived = Packet()
        data = str(data)
        flags = bin(data[: 2])
        pktReceived.header['ack'] = int(flags[6])
        pktReceived.header['rst'] = int(flags[7])
        pktReceived.header['chk'] = int(flags[7])
    
    def sendSUDP(self, data):
        chunkSize = 65000
        dataSize = len(data)
        if self.senderNextSeqNum % self.MSS < (self.senderBase + self.senderWindowSize) % self.MSS:
            if dataSize:
                i = 0
                while (i + 1) * chunkSize < dataSize:
                    chunk = data[i * chunkSize: (i + 1) * chunkSize]
                    pkt = Packet(data, self.senderNextSeqNum % self.MSS)
                    pkt.packet = pkt.makePacket()
                    self.sendPacket(pkt.packet)
                    # start timer(self.senderNextSeqNum % self.MSS)
                    if senderBuffer[self.senderNextSeqNum % self.MSS] == 0:
                        self.senderBuffer[self.senderNextSeqNum % self.MSS] = 1
                    else:
                        print('There is a problem with the Sender Buffer')
                    self.senderNextSeqNum = ((self.senderNextSeqNum % self.MSS) + 1) % self.MSS
                    i += 1
            else:
                pkt = Packet(data, self.senderNextSeqNum, ack=False, rst=True)
                pkt.packet = pkt.makePacket()
                self.sendPacket(pkt.packet)
                # start timer(self.senderNextSeqNum % self.MSS)
                if senderBuffer[self.senderNextSeqNum % self.MSS] == 0:
                    self.senderBuffer[self.senderNextSeqNum % self.MSS] = 1
                else:
                    print('There is a problem with the Sender Buffer')
                self.senderNextSeqNum = (self.senderNextSeqNum + 1) % self.MSS
        else:
            print('packet not sent. Buffer is full.')
    
    def deliver_data(self, data):
        print(data)

    def receiveSUDP(self):
        rcvData, addr = self.recvSocket.recvfrom(RECV_BUFF_SIZE)
        pkt = self.setPacket(rcvData)
        if pkt.header['checksum'] == Packet().getChecksum(pkt.data):
            self.receiverSeqNum = pkt.header['seqNum']
            if self.receiverBase < (self.receiverBase + self.receiverWindowSize) % self.MSS:
                if(self.receiverBase < self.receiverSeqNum < (self.receiverBase + self.receiverWindowSize) % self.MSS):
                    self.receiverStatusBuffer[self.receiverSeqNum] = 1
                    self.receiverDataBuffer[self.receiverSeqNum] = pkt.data
                    ackPacket = Packet(self.receiverSeqNum, ack=True)
                    ackPacket.packet = ackPacket.makePacket()
                    self.sendPacket(ackPacket.packet, addr)
            elif (self.receiverBase == self.receiverSeqNum):
                self.receiverStatusBuffer[self.receiverSeqNum] = 1
                self.receiverDataBuffer[self.receiverSeqNum] = pkt.data
                ackPacket = Packet(self.receiverSeqNum, ack=True)
                ackPacket.packet = ackPacket.makePacket()
                self.sendPacket(ackPacket.packet, addr)
                
                j = self.receiverBase
                while(self.receiverStatusBuffer[j % self.MSS] == 1):
                    self.receiverStatusBuffer[(j + self.receiverWindowSize) % self.MSS] = 0
                    self.receiverDataBuffer[(j + self.receiverWindowSize) % self.MSS] = ''
                    self.deliver_data(self.receiverDataBuffer[j % self.MSS])
                    j += 1
                self.receiverBase = j % self.MSS
            else:
                if((self.receiverBase < self.receiverSeqNum < self.MSS) or 
                   (0 <= self.receiverSeqNum < (self.receiverBase + self.receiverWindowSize % self.MSS))):
                    self.receiverStatusBuffer[self.receiverSeqNum] = 1
                    self.receiverStatusBuffer[self.receiverSeqNum] = 1
                    self.receiverDataBuffer[self.receiverSeqNum] = pkt.data
                    ackPacket = Packet(self.receiverSeqNum, ack=True)
                    ackPacket.packet = ackPacket.makePacket()
                    self.sendPacket(ackPacket.packet, addr)

# %%
sender = SUDP(ip='127.0.0.1')
receiver = SUDP(ip='127.0.0.1')
sender.sendSUDP('Hello Kitty')
receiver.receiveSUDP()
=======
# %%
import math
import socket
import hashlib
import threading
import time

class Packet:
    def __init__(self, data='', seqNum=0, ack=False, rst=False):

        self.data = data
        self.header = {"ack": 1 if ack else 0,
                       "rst": 1 if rst else 0,
                       "chk": 0,
                       "seqNum": seqNum,
                       "checkSum": self.getChecksum(self.data), # 64 bytes in length
                       "packetLength": len(self.data) + 74} # 6 bytes
        self.packet = ''

    def makePacket(self):
        non_data_str = "00000" + str(self.header['ack']) + str(self.header['rst']) + str(self.header['chk']) + "~~" + str(self.header['seqNum']) + "~~" + str(self.header['checkSum']) + "~~" + str(self.header['packetLength']) + "~~"
        non_data_64 = bytes(non_data_str, 'utf-8')
        return non_data_str + byte64.decodebytes(self.data)

    def getChecksum(self, data):
        return hashlib.sha256(str(data).encode()).hexdigest()

class client:

    def __init__(self,serverIP,serverPort):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = serverIP
        self.port = serverPort
        self.allPackets = None
        # self.message = packet

    def send(self):
        # IMPLEMENT SELECTIVE REPEAT HERE!!!
        filename = str(input('Enter the name of file you want to send:'))
        packets = self.makePacketList(filename)
        # print(packets)
        for packet in packets:
            self.udpSocket.sendto(bytes(packet,'utf-8'), (self.ip,self.port))
            print('packet sent')
        # the sending object shd be of bytes format.
        print("Total Msg sent first time")
        while(True):
            reply = self.udpSocket.recvfrom(4096)
            message = reply[0]
            address = reply[1]
            serverMsg = "Message from Server:{}".format(message)
            serverIP  = "Server IP Address:{}".format(address)
            print(serverMsg)
            # print(serverIP)
            message = message.decode().split("~~")
            # message[0] = flagbits, [0][6] = rst, [0][5] = ack, [0][7] = chk
            # message[1] = seqnum
            # message[2] = checkSum
            # message[3] = packetLength
            # message[4] = data
            if(message[0][6] == "1" and message[1] == "-1" and message[0][5] != "1"):
                # self.udpSocket.sendto(str("reset Pcket received..! Now F off").encode(), address)
                print("Complete transfer successfull")
                break
            elif(message[1] == "-1" and message[0][5] == "1" and message[0][6] == "1"):
                # We have received the list of dropped packets in data.
                print("Dropped packets are:",message[4].split(';')[:-1])
                for i in message[4].split(';')[:-1]:
                    print("Resending packet", i)
                    self.udpSocket.sendto(bytes(self.allPackets[int(i)],'utf-8'), (self.ip,self.port))
                self.udpSocket.sendto(Packet("",-1,rst=True).makePacket().encode(), address)

        print("Closing connection to server.")
        self.udpSocket.close()

    def makePacketList(self,filename):
        packetList = list()

        seq = 0
        chunkSize = 1024
        fo = open(filename,"rb").read()
        parts = list()

        while(True):
            part = fo.read(chunkSize)
            if not part:
                break
            else:
                parts.append(part)
                print("Data length is",len(part))

        for part in parts:
            tempPkt = Packet(part, seq).makePacket()
            packetList.append(tempPkt)
            print("Packet length is",len(tempPkt))
            seq += 1

        #insert reset packet to end the connection
        packetList.append(Packet("",-1,rst=True).makePacket())
        self.allPackets = list(packetList)
        self.allPackets.pop()
        return packetList

class server:
    localIP = "127.0.0.1"
    localPort = 20001
    def __init__(self):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind((self.localIP,self.localPort))
        print("Server is up!")

    def listen(self):
        recvBuffer = list()
        recvSeqBuffer = list() #Stores the received seqnum's in order
        # HANDLE SENDING ACK'S HERE! AND STORING RECEIVED DATA INTO BUFFERS.

        while(True):
            bytesAddressPair = self.udpSocket.recvfrom(4096)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            clientMsg = "Message from Client:{}".format(message)
            clientIP  = "Client IP Address:{}".format(address)
            message = message.decode().split("~~")
            # message[0] = flagbits, [0][6] = rst, [0][5] = ack, [0][7] = chk
            # message[1] = seqnum
            # message[2] = checkSum
            # message[3] = packetLength
            # message[4] = data
            if(message[0][6] == "1"):
                print("Client sent rst packet. Checking for missing packets...")
                # we have received a rst packet ==> client is done sending.
                # check if we have received every packet.

                #### HANDLE THE CASE IN CLIENT WHERE THIS RST PACKAGE GETS DROPPED
                missingSeqNum = list()
                Max = max(recvSeqBuffer)+1
                for i in range(Max):
                    if i not in recvSeqBuffer:
                        missingSeqNum.append(i)

                if len(missingSeqNum) == 0:
                    # we have received every packet. send an rst message to client to stop
                    # further sending msgs.
                    print("No packets dropped.. sending rst packet to client!!! yayy.. ;)")
                    rstPacket = Packet("",-1, rst=True).makePacket().encode()
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
                    drpdPackets = Packet(drpdData,-1, ack=True, rst=True).makePacket().encode()
                    print('Data', drpdPackets)
                    self.udpSocket.sendto(drpdPackets, address)
                    print('Server sent request for missing packets\n')
            else:
                if hashlib.sha256(message[4].encode()).hexdigest() == message[2]:
                    print("Received packet",message[1])
                    # handles duplicates	
                    if(int(message[1]) not in recvSeqBuffer):
                        recvBuffer.append(message[4])
                        recvSeqBuffer.append(int(message[1]))
                    # ackPacket = Packet("",message[1],ack=True).makePacket().encode()
                    # self.udpSocket.sendto(ackPacket, address)

        # ASSUMING SUCCESSFULL RECEIVE OF ALL DATA. REORDER THEM AND WRITE TO FILE.
        print("Closing connection.. bye bye client")
        self.udpSocket.close()

        print("Writing to received.txt....")
        maxi = max(recvSeqBuffer)+1
        #### SHD HANDLE MULTIPLE TYPES OF FILES
        f = open("received.txt", "w")
        for i in range(maxi):
            index = recvSeqBuffer.index(i)
            f.write(recvBuffer[index])
        print("Write succesfull... goodbye...")
>>>>>>> Stashed changes
