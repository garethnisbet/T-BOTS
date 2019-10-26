import threading
lock = threading.Lock()
x = 0
def foo():
    global x
    for i in xrange(1000000):
        with lock:    # Uncomment this to get the right answer
            x += 1
def foo2():
    global x
    for i in xrange(1000000):
        with lock:    # Uncomment this to get the right answer
            x += 2
threads = [threading.Thread(target=foo), threading.Thread(target=foo2)]
for t in threads:
    t.daemon = True    #runs without blocking the main program from exiting. And when main program exits, associated daemon threads are killed too. 
    t.start()
for t in threads:
    t.join()

print(x)
