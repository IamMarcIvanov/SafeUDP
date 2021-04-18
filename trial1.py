# # %%
# import random

# with open('sample2.txt', 'w') as f:
#     for i in range(100000):
#         f.write(chr(random.randint(97, 97+25)))

# # %%
# import base64

# infile = "i1.jpg"
# l = []
# data = open(infile, "rb").read()
# i = 0
# while True: 
#     e = base64.encodebytes(data[20 * i : (i + 1) * 20])
#     if not e:
#         break
#     else:
#         l.append(e)
#     i += 1


# outfile = infile.split('.')[0] + 'out.' + infile.split('.')[1]
# with open(outfile, 'wb') as f:
#     for e in l:
#         f.write(base64.decodebytes(e))

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

import base64

print(base64.encodebytes(bytes('hello', 'utf-8')))
