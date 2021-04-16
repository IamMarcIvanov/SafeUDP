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
        n_add0_seqNum = 3 - len(str(self.header['seqNum']))
        n_add0_pkt_len = 6 - len(str(len(self.data) + 74))
        headerStr = str(flags) + '0' * n_add0_seqNum + str(self.header['seqNum']) + str(self.header['checkSum']) + '0' * n_add0_pkt_len + str(self.header['packetLength'])
        return headerStr + self.data

    def getChecksum(self, data):
        return hashlib.sha256(str(data).encode()).hexdigest()

class client:
    def __init__(self,serverIP,serverPort):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = serverIP
        self.port = serverPort
        # self.message = packet

    def send(self):
        # IMPLEMENT SELECTIVE REPEAT HERE!!!
        filename = str(input('Enter the name of file you want to send:'))
        packets = self.makePacketList(filename)
        for packet in packets:
            self.udpSocket.sendto(bytes(packet,'utf-8'), (self.ip,self.port))
            print('packet sent')
        # the sending object shd be of bytes format.
        print("Total Msg sent")

    def makePacketList(self,filename):
        packetList = list()

        seq = 0
        chunkSize = 50
        fo = open(filename,"r")
        parts = list()

        while(True):
            part = fo.read(chunkSize)
            if not part:
                break
            else:
                parts.append(part)

        for part in parts:
            print('part',seq,':',part)
            tempPkt = Packet(part,seq).makePacket()
            print('appending:',tempPkt)
            packetList.append(tempPkt)
            seq += 1

        return packetList

    def recv(self):
        reply = self.udpSocket.recvfrom(RECV_BUFF_SIZE)
        print("reply from server:",reply[0])

class server:
    localIP = "127.0.0.1"
    localPort = 20001
    def __init__(self):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind((self.localIP,self.localPort))
        print("Server is up!")

    def listen(self):
        # HANDLE SENDING ACK'S HERE! AND STORING RECEIVED DATA INTO BUFFERS.
        while(True):
            bytesAddressPair = self.udpSocket.recvfrom(RECV_BUFF_SIZE)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            clientMsg = "Message from Client:{}".format(message)
            clientIP  = "Client IP Address:{}".format(address)
            fo = open("received.txt","a")
            # # 68 because first 4 bits are flag bits and next 64 is checksum
            fo.write(str(message[70:-1])) # Properly write the data only to a file.
            print(clientMsg)
            print(clientIP)

            self.udpSocket.sendto(str("Pcket reeived..! Now F off").encode(), address)

# class Sender:
#     def __init__(self, ip):
#         self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.sendSocket.bind((str(self.receiverIP), SERV_PORT))
#         self.sendSocket.setblocking(0)
#         self.senderNextSeqNum = 0
#         self.MSS = MAX_SEG_SIZE
#         self.senderBuffer = [0] * self.MSS
#         self.senderWindowSize = SENDER_WINDOW_SIZE
#         self.senderBase = 0
#         # 0 means unsent
#         # 1 means sent but ack not received
#         # 2 means sent and ack received
#
#         self.receiverStatusBuffer = [0] * self.MSS
#         self.receiverDataBuffer = [0] * self.MSS
#         self.receiverWindowSize = RECEIVER_WINDOW_SIZE
#         self.receiverBase = 0
#         self.receiverSeqNum = 0
#         # 0 means not received
#         # 1 means sent ack
#
#     def sendPacket(self, data, ip):
#         self.sendSocket.sendto(bytes(data.encode('utf-8')), (ip, RECV_PORT))
#
#     def setPacket(self, data):
#         pktReceived = Packet()
#         data = str(data)
#         flags = bin(data[: 2])
#         pktReceived.header['ack'] = int(flags[6])
#         pktReceived.header['rst'] = int(flags[7])
#         pktReceived.header['chk'] = int(flags[7])
#
#     def sendSUDP(self, data):
#         chunkSize = 65000
#         dataSize = len(data)
#         if self.senderNextSeqNum % self.MSS < (self.senderBase + self.senderWindowSize) % self.MSS:
#             if dataSize:
#                 i = 0
#                 while (i + 1) * chunkSize < dataSize:
#                     chunk = data[i * chunkSize: (i + 1) * chunkSize]
#                     pkt = Packet(data, self.senderNextSeqNum % self.MSS)
#                     pkt.packet = pkt.makePacket()
#                     self.sendPacket(pkt.packet)
#                     # start timer(self.senderNextSeqNum % self.MSS)
#                     if senderBuffer[self.senderNextSeqNum % self.MSS] == 0:
#                         self.senderBuffer[self.senderNextSeqNum % self.MSS] = 1
#                     else:
#                         print('There is a problem with the Sender Buffer')
#                     self.senderNextSeqNum = ((self.senderNextSeqNum % self.MSS) + 1) % self.MSS
#                     i += 1
#             else:
#                 pkt = Packet(data, self.senderNextSeqNum, ack=False, rst=True)
#                 pkt.packet = pkt.makePacket()
#                 self.sendPacket(pkt.packet)
#                 # start timer(self.senderNextSeqNum % self.MSS)
#                 if senderBuffer[self.senderNextSeqNum % self.MSS] == 0:
#                     self.senderBuffer[self.senderNextSeqNum % self.MSS] = 1
#                 else:
#                     print('There is a problem with the Sender Buffer')
#                 self.senderNextSeqNum = (self.senderNextSeqNum + 1) % self.MSS
#         else:
#             print('packet not sent. Buffer is full.')
#
#     def deliver_data(self, data):
#         print(data)
#
#     def receiveSUDP(self):
#         rcvData, addr = self.recvSocket.recvfrom(RECV_BUFF_SIZE)
#         pkt = self.setPacket(rcvData)
#         if pkt.header['checksum'] == Packet().getChecksum(pkt.data):
#             self.receiverSeqNum = pkt.header['seqNum']
#             if self.receiverBase < (self.receiverBase + self.receiverWindowSize) % self.MSS:
#                 if(self.receiverBase < self.receiverSeqNum < (self.receiverBase + self.receiverWindowSize) % self.MSS):
#                     self.receiverStatusBuffer[self.receiverSeqNum] = 1
#                     self.receiverDataBuffer[self.receiverSeqNum] = pkt.data
#                     ackPacket = Packet(self.receiverSeqNum, ack=True)
#                     ackPacket.packet = ackPacket.makePacket()
#                     self.sendPacket(ackPacket.packet, addr)
#             elif (self.receiverBase == self.receiverSeqNum):
#                 self.receiverStatusBuffer[self.receiverSeqNum] = 1
#                 self.receiverDataBuffer[self.receiverSeqNum] = pkt.data
#                 ackPacket = Packet(self.receiverSeqNum, ack=True)
#                 ackPacket.packet = ackPacket.makePacket()
#                 self.sendPacket(ackPacket.packet, addr)
#
#                 j = self.receiverBase
#                 while(self.receiverStatusBuffer[j % self.MSS] == 1):
#                     self.receiverStatusBuffer[(j + self.receiverWindowSize) % self.MSS] = 0
#                     self.receiverDataBuffer[(j + self.receiverWindowSize) % self.MSS] = ''
#                     self.deliver_data(self.receiverDataBuffer[j % self.MSS])
#                     j += 1
#                 self.receiverBase = j % self.MSS
#             else:
#                 if((self.receiverBase < self.receiverSeqNum < self.MSS) or
#                    (0 <= self.receiverSeqNum < (self.receiverBase + self.receiverWindowSize % self.MSS))):
#                     self.receiverStatusBuffer[self.receiverSeqNum] = 1
#                     self.receiverStatusBuffer[self.receiverSeqNum] = 1
#                     self.receiverDataBuffer[self.receiverSeqNum] = pkt.data
#                     ackPacket = Packet(self.receiverSeqNum, ack=True)
#                     ackPacket.packet = ackPacket.makePacket()
#                     self.sendPacket(ackPacket.packet, addr)
