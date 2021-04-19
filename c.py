import sudp2 as s
import time

if __name__ == '__main__':
    start_time = time.time()

    r = s.client('127.0.0.1', 20001)
    r.send()

    end_time = time.time()
    print('elapsed time: ', end_time - start_time)
