from task1 import BufferManager
import threading
import time

# -----------------------------
# Producer-Consumer using BM's double buffers
# -----------------------------
lock = threading.Lock()
done = False  # Flag to indicate producer finished

def producer(bm):
    """Read from BufferManager and mark done when EOF is reached"""
    global done
    while True:
        ch = bm.getNextChar()
        if ch is None:
            break
        # simulate reading delay
        time.sleep(0.01)
    done = True  # EOF reached
    print("\n*** Producer finished reading file ***")

def consumer(bm):
    """Process characters from BufferManager"""
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
        time.sleep(0.02)  # simulate processing delay

# -----------------------------
# Main
# -----------------------------
def main():
    bm = BufferManager("tasksampel.cpp", buffer_size=8)

    # Create threads
    t1 = threading.Thread(target=producer, args=(bm,))
    t2 = threading.Thread(target=consumer, args=(bm,))

    # Start threads
    t1.start()
    t2.start()

    # Wait for threads to finish
    t1.join()
    t2.join()

    print("\nDone (Task 2 with double buffers)")
    print("Total buffer switches:", bm.switch_count)

if __name__ == "__main__":
    main()
