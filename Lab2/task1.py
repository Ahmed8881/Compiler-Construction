
SENTINEL = None


class BufferManager:

    def __init__(self, filename, buffer_size=8):

        self.file = open(filename, "r")

        self.buffer_size = buffer_size

        self.buffer1 = []
        self.buffer2 = []

        self.active = 1     # 1 = buffer1, 2 = buffer2
        self.forward = 0

        self.eof = False
        self.switch_count = 0

        print("\nFilling buffers first time...")

        self.fill_buffer(1)
        self.fill_buffer(2)

        print("------------------------------------")

    # --------------------------------
    # Fill buffer from file
    # --------------------------------
    def fill_buffer(self, which):

        data = self.file.read(self.buffer_size)

        buf = list(data)
        buf.append(SENTINEL)

        if which == 1:
            self.buffer1 = buf
            print("Buffer 1 filled with:", repr("".join(c for c in buf if c is not None)))
        else:
            self.buffer2 = buf
            print("Buffer 2 filled with:", repr("".join(c for c in buf if c is not None)))

        if data == "":
            self.eof = True

    # --------------------------------
    # Return active buffer
    # --------------------------------
    def get_active_buffer(self):

        if self.active == 1:
            return self.buffer1
        else:
            return self.buffer2

    # --------------------------------
    # Switch buffer
    # --------------------------------
    def switch_buffer(self):

        print("\n*** Buffer End Reached ***")

        if self.active == 1:
            print("Switching from Buffer 1 to Buffer 2")
            self.active = 2
            self.fill_buffer(1)
        else:
            print("Switching from Buffer 2 to Buffer 1")
            self.active = 1
            self.fill_buffer(2)

        self.forward = 0
        self.switch_count += 1

        print("Now active buffer =", self.active)
        print("------------------------------------")

    # --------------------------------
    # Get next character
    # --------------------------------
    def getNextChar(self):

        buf = self.get_active_buffer()
        ch = buf[self.forward]

        if ch is SENTINEL:

            if self.eof:
                print("\n*** EOF reached ***")
                return None

            self.switch_buffer()
            return self.getNextChar()

        print(f"[Buffer {self.active}] Read char -> '{ch}' (index {self.forward})")

        self.forward += 1
        return ch


# --------------------------------
# Demo
# --------------------------------
def main():

    bm = BufferManager("tasksampel.cpp", buffer_size=8)

    print("\nReading file using double buffering\n")

    while True:

        ch = bm.getNextChar()

        if ch is None:
            break

    print("\nFinished reading file.")
    print("Total buffer switches:", bm.switch_count)


if __name__ == "__main__":
    main()
