# task2.py

from task1 import BufferManager
import threading
import time


# -----------------------------
# Shared buffer (between threads)
# -----------------------------
shared_buffer = []
BUFFER_LIMIT = 10

empty = threading.Semaphore(BUFFER_LIMIT)
full = threading.Semaphore(0)

lock = threading.Lock()

done = False


# -----------------------------
# Producer thread
# Reads characters from file
# -----------------------------
def producer(bm):

    global done

    while True:

        ch = bm.getNextChar()

        if ch is None:
            break

        empty.acquire()

        lock.acquire()
        shared_buffer.append(ch)
        lock.release()

        full.release()

        time.sleep(0.01)

    # tell consumer that producer is finished
    done = True
    full.release()


# -----------------------------
# Consumer thread
# Processes characters
# -----------------------------
def consumer():

    global done

    print("\nScanner started\n")

    while True:

        full.acquire()

        lock.acquire()

        if len(shared_buffer) == 0:

            lock.release()

            if done:
                break
            else:
                continue

        ch = shared_buffer.pop(0)

        lock.release()

        empty.release()

        # processing (very simple scanner)
        print("Scanned ->", repr(ch))

        time.sleep(0.02)


# -----------------------------
# Main
# -----------------------------
def main():

    bm = BufferManager("tasksampel.cpp", buffer_size=8)

    t1 = threading.Thread(target=producer, args=(bm,))
    t2 = threading.Thread(target=consumer)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("\nDone (Task 2)")
    print("Total buffer switches:", bm.switch_count)


if __name__ == "__main__":
    main()
