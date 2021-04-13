import math
import socket

MAX_SEG_SIZE = 256
SENDER_WINDOW_SIZE = 50
PORT = 12345
RECEIVER_WINDOW_SIZE = 50
RECV_BUFF = 4096

class Packet:
    def __init__(self, data, seqNum, ack=False, rst=False):
        self.data = data # the data that the user client wants to send. Text string.
        self.header = {"ack": 1 if ack else 0,
                       "rst": 1 if rst else 0,
                       "chk": 0, # 0 means checksum of just the data
                       "seqNum": seqNum,
                       "checkSum": self.getChecksum(),
                       "packetLength": self.getSize()} # 6 bytes
        self.packet = self.makePacket()
        
    def makePacket(self):
        flags = int("00000" + str(self.header['ack']) + str(self.header['rst']) + str(self.header['chk']), 2)
        headerStr = str(flags) + str(self.header['seqNum']) + str(self.header['checkSum']) + str(self.header['packetLength'])
        return headerStr + data
    
    def getChecksum(self):
        return str(00)
    
    def getSize(self):
        k = len(str(len(data) + 10))
        if k < 5:
            return "0" * (5-k) + str(len(data) + 10)
        else:
            return str(len(data) + 10)
    

class SUDP:
    def __init__(self, udp_socket, ip):
        self.receiverIP = ip
        self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendSocket.bind(str(self.receiverIP), PORT)
        self.senderNextSeqNum = 0
        self.MSS = MAX_SEG_SIZE
        self.senderBuffer = [0] * self.MSS
        self.senderWindowSize = SENDER_WINDOW_SIZE
        self.senderBase = 0
        
        self.receiverBuffer = [0] * self.MSS
        self.receiverWindowSize = RECEIVER_WINDOW_SIZE
        self.receiverBase = 0
        self.receiverSeqNum = 0
        # 0 means unsent
        # 1 means sent but ack not received
        # 2 means sent and ack received
    
    def sendPacket(self, data):
        self.sendSocket.sendto(bytes(data.encode('utf-8')), (self.receiverIP, PORT))
        
    def sendSUDP(self, data):
        #UDP size 65000 bytes
        chunkSize = 65000
        dataSize = len(data)
        if self.senderNextSeqNum % self.MSS < (self.senderBase + self.senderWindowSize) % self.MSS:
            if dataSize:
                i = 0
                while (i + 1) * chunkSize < dataSize:
                    chunk = data[i * chunkSize: (i + 1) * chunkSize]
                    pkt = Packet(data, self.senderNextSeqNum % self.MSS)
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
                # self.sendPacket(pkt)
                # start timer(self.senderNextSeqNum % self.MSS)
                if senderBuffer[self.senderNextSeqNum % self.MSS] == 0:
                    self.senderBuffer[self.senderNextSeqNum % self.MSS] = 1
                else:
                    print('There is a problem with the Sender Buffer')
                self.senderNextSeqNum = (self.senderNextSeqNum + 1) % self.MSS
        else:
            print('packet not sent. Buffer is full.')
    
    def receiveSUDP(self, ):
        rcvData, addr = self.recvSocket.recvfrom(RECV_BUFF)
        rcvData = str(rcvData)
        if not self.isCorrupt(rcvData):
            self.receiverSeqNum = self.getSeqNum(rcvData)

class sendSUDP(SUDP, Packet):
    def __init__(self, udp_socket, pkt):
        self.super().__init__(udp_socket, pkt)
        self.send_buff = None #binary string of buffer that we are sending
        self.send_win = []
        self.window_size
        
