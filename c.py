import SUDP as s

if __name__ == '__main__':
    r = s.client('127.0.0.1',20001)
    r.send()
