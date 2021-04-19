import SUDP as s
pkt = s.Packet("",0)
fo = open("sample.gif", "rb")
pkt.data = fo.read(10)
print(type(pkt.data))
