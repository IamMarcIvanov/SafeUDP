import math


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
    def __init__(self, udp_socket, pkt):
        self.socket = udp_socket # UDP socket object
        self.packet = pkt
        self.senderNextSeqNum = 0
        self.MSS = 256
        self.senderBuffer = [0] * self.MSS
        self.senderWindowSize = 50
        self.senderBase = 0
        # 0 means unsent
        # 1 means sent but ack not received
        # 2 means sent and ack received
    
    def sendSUDP(self, data, ip):
        #UDP size 65000 bytes
        #data = data.encode('utf-8')
        chunkSize = 65000
        dataSize = len(data)
        if dataSize:
            i = 0
            while (i + 1) * chunkSize < dataSize:
                chunk = data[i * chunkSize: (i + 1) * chunkSize]
                pkt = Packet(data, seqNum)
                seqNum = 
                i += 1
        else:
            pkt = Packet(data, seqNum, )
            

class sendSUDP(SUDP, Packet):
    def __init__(self, udp_socket, pkt):
        self.super().__init__(udp_socket, pkt)
        self.send_buff = None #binary string of buffer that we are sending
        self.send_win = []
        self.window_size
        
BUFF_SIZE = 1024
