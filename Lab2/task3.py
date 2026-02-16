# -----------------------------
# Task 3: Character Stream Interface
# -----------------------------
SENTINEL = None

class CharStream:
    def __init__(self, filename, buffer_size=16):
        self.file = open(filename, "r")
        self.buffer_size = buffer_size

        # Two buffers
        self.buffer1 = []
        self.buffer2 = []

        # Buffer state
        self.active = 1       # 1 = buffer1, 2 = buffer2
        self.forward = 0      # current reading position
        self.lexemeBegin = 0  # start of current lexeme

        # EOF and stats
        self.eof = False
        self.switch_count = 0

        # Fill buffers initially
        self.fill_buffer(1)
        self.fill_buffer(2)

    # -----------------------------
    # Fill a buffer from file
    # -----------------------------
    def fill_buffer(self, which):
        data = self.file.read(self.buffer_size)
        buf = list(data)
        buf.append(SENTINEL)

        if which == 1:
            self.buffer1 = buf
        else:
            self.buffer2 = buf

        if data == "":
            self.eof = True

    # -----------------------------
    # Get active buffer
    # -----------------------------
    def get_active_buffer(self):
        return self.buffer1 if self.active == 1 else self.buffer2

    # -----------------------------
    # Switch buffer
    # -----------------------------
    def switch_buffer(self):
        self.active = 2 if self.active == 1 else 1
        self.fill_buffer(1 if self.active == 2 else 2)
        self.forward = 0
        self.switch_count += 1
        print(f"\n--- Buffer switched to Buffer {self.active} ---")

    # -----------------------------
    # Get next character
    # -----------------------------
    def getNextChar(self):
        buf = self.get_active_buffer()
        ch = buf[self.forward]

        if ch is SENTINEL:
            if self.eof:
                return None
            self.switch_buffer()
            return self.getNextChar()

        self.forward += 1
        return ch

    # -----------------------------
    # Move back one character
    # -----------------------------
    def ungetChar(self):
        if self.forward > 0:
            self.forward -= 1
        else:
            print("Warning: Cannot unget at buffer start")

    # -----------------------------
    # Get current lexeme string
    # -----------------------------
    def getLexeme(self):
        buf = self.get_active_buffer()
        start = self.lexemeBegin
        end = self.forward
        lexeme_chars = []

        for i in range(start, end):
            if buf[i] is not SENTINEL:
                lexeme_chars.append(buf[i])
        return ''.join(lexeme_chars)

    # -----------------------------
    # Reset lexeme start
    # -----------------------------
    def resetLexemeBegin(self):
        self.lexemeBegin = self.forward

# -----------------------------
# Demo
# -----------------------------
def main():
    stream = CharStream("tasksampel.cpp", buffer_size=16)
    print("Reading file with CharStream Interface\n")

    while True:
        ch = stream.getNextChar()
        if ch is None:
            break
        print(ch, end="")

        # Example usage: every 8 chars, show lexeme and reset
        if stream.forward % 8 == 0:
            lex = stream.getLexeme()
            print(f"\n[Lexeme so far: '{lex}']")
            stream.resetLexemeBegin()

    print("\n\nFinished reading file.")
    print("Total buffer switches:", stream.switch_count)

if __name__ == "__main__":
    main()
