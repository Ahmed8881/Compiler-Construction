from task1 import BufferManager
import threading
import time


lock = threading.Lock()
done = False  

def producer(bm):
    global done
    while True:
        ch = bm.getNextChar()
        if ch is None:
            break
        time.sleep(0.01)
    done = True  # EOF reached
    print("\n*** Producer finished reading file ***")

def consumer(bm):
    global done
    print("\nScanner started\n")
    while True:
        with lock:
            ch = bm.getNextChar()
        if ch is None:
            if done:
                break
            else:
                continue
        print("Scanned ->", repr(ch))
        time.sleep(0.02)  


def main():
    bm = BufferManager("tasksampel.cpp", buffer_size=8)
    t1 = threading.Thread(target=producer, args=(bm,))
    t2 = threading.Thread(target=consumer, args=(bm,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("\nDone (Task 2 with double buffers)")
    print("Total buffer switches:", bm.switch_count)

if __name__ == "__main__":
    main()
