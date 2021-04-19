# # %%
# import random

# with open('sample2.txt', 'w') as f:
#     for i in range(100000):
#         f.write(chr(random.randint(97, 97+25)))

# %%
import base64

infile = "i1.jpg"
l = []
data = open(infile, "rb").read()
i = 0
while True: 
    e = base64.encodebytes(data[20 * i : (i + 1) * 20])
    if not e:
        break
    else:
        l.append(e)
    i += 1

decoded = b''
outfile = infile.split('.')[0] + 'out.' + infile.split('.')[1]
with open(outfile, 'wb') as f:
    for e in l:
        k = base64.decodebytes(e)
        f.write(k)
        decoded += k

print(decoded.count(b''))

# # %%
# s = bytes('a~b', 'utf-8')
# l = s.split(b'~')
# print(l)

# # %%
# import threading
# import time

# def hello():
#     print('string')

# t = threading.Timer(5, hello)
# t.start()

# time.sleep(1)
    
# t.cancel()

# # %%
# import threading

# x = 0
# def t1():
#     global x
#     x = 1

# try:
#     threading.Thread(target=t1)
# except:
#     print('could not start thread')
# finally:
#     print(x)
# %%
import base64

a = base64.encodebytes(bytes('hello', 'utf-8'))
b = base64.decodebytes(a)
print(b + b'super mario')
print(bytes('hello', 'utf-8'))
print(b)
print(str(b))

# %%
a = [1, 2, 3]
b = list(a)
print(b)
