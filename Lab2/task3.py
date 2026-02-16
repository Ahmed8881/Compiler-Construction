# Task 3: Character Stream Interface (Enhanced)
import os
import sys
import time
from pathlib import Path
from typing import Optional

lab1_dir = Path(__file__).resolve().parents[1] / "Lab1"
if str(lab1_dir) not in sys.path:
    sys.path.insert(0, str(lab1_dir))
try:
    from task1 import tokenize_expression
except Exception:
    def tokenize_expression(s):
        return ["(tokenizer-not-available)"]

SENTINEL = None


class CharStream:
    def __init__(self, filename: str, buffer_size: int = 4096):
        self.filename = filename
        self.file = open(filename, "r", encoding="utf-8", errors="ignore")
        self.buffer_size = buffer_size

        # For computing file size (for reporting)
        try:
            self.total_file_size = os.path.getsize(filename)
        except Exception:
            self.total_file_size = -1

        # Two buffers and their start offsets
        self.buffer1 = []
        self.buffer2 = []
        self.buffer1_start = 0
        self.buffer2_start = 0

        # File read offset (how many bytes/characters consumed from file by fills)
        self.file_offset = 0

        # Buffer state
        self.active = 1  # 1 = buffer1, 2 = buffer2
        self.forward = 0  # index into active buffer

        # Lexeme tracking (absolute positions)
        self.absolute_pos = 0
        self.lexemeBegin = 0

        # EOF and stats
        self.eof = False
        self.switch_count = 0
        self.fill_durations = []
        self.transitions = []  # store transition demo entries

        # Initially fill both buffers
        self.fill_buffer(1)
        self.fill_buffer(2)

    # -----------------------------
    # Fill a buffer from file and measure time
    # -----------------------------
    def fill_buffer(self, which: int):
        start_time = time.perf_counter()
        start_offset = self.file_offset
        data = self.file.read(self.buffer_size)
        data_len = len(data)
        buf = list(data)
        buf.append(SENTINEL)

        if which == 1:
            self.buffer1 = buf
            self.buffer1_start = start_offset
        else:
            self.buffer2 = buf
            self.buffer2_start = start_offset

        self.file_offset += data_len

        if data == "":
            self.eof = True

        duration = (time.perf_counter() - start_time) * 1000.0
        self.fill_durations.append(duration)
        return duration

    # -----------------------------
    # Get active buffer and its start offset
    # -----------------------------
    def get_active_buffer(self):
        if self.active == 1:
            return self.buffer1, self.buffer1_start
        else:
            return self.buffer2, self.buffer2_start

    # -----------------------------
    # Switch buffer and record a transition entry
    # -----------------------------
    def switch_buffer(self):
        # Capture info before switch for demo
        old_active = self.active
        old_buf, old_start = (self.buffer1, self.buffer1_start) if old_active == 1 else (self.buffer2, self.buffer2_start)
        old_index = self.forward

        # compute absolute position at boundary
        boundary_pos = old_start + old_index

        # perform switch
        self.active = 2 if self.active == 1 else 1
        # Refill the now-inactive buffer (same logic as typical double buffering)
        to_fill = 1 if self.active == 2 else 2
        fill_dur = self.fill_buffer(to_fill)

        # reset forward for new active buffer
        self.forward = 0
        self.switch_count += 1

        # Capture a few chars around the boundary for demo (safely)
        demo = {}
        demo['switch_at_absolute'] = boundary_pos
        demo['old_active'] = old_active
        demo['new_active'] = self.active

        # last few chars from old buffer
        last_chars = []
        for i in range(max(0, old_index - 6), old_index):
            if i < len(old_buf) and old_buf[i] is not SENTINEL:
                last_chars.append(old_buf[i])
        demo['old_tail'] = last_chars

        # first few chars from new active buffer
        new_buf, new_start = self.get_active_buffer()
        first_chars = []
        for i in range(0, min(8, len(new_buf))):
            if new_buf[i] is not SENTINEL:
                first_chars.append(new_buf[i])
        demo['new_head'] = first_chars
        demo['fill_time_ms'] = fill_dur

        self.transitions.append(demo)

    # -----------------------------
    # Get next character (public API: char getNextChar())
    # -----------------------------
    def getNextChar(self) -> Optional[str]:
        buf, start = self.get_active_buffer()
        if self.forward >= len(buf):
            return None

        ch = buf[self.forward]
        if ch is SENTINEL:
            if self.eof:
                return None
            self.switch_buffer()
            return self.getNextChar()

        # Return character and advance absolute and forward
        self.forward += 1
        self.absolute_pos += 1
        return ch

    # -----------------------------
    # Unget one character (public API: void ungetChar())
    # -----------------------------
    def ungetChar(self):
        if self.absolute_pos == 0:
            return
        # move absolute_pos back
        self.absolute_pos -= 1
        # figure out which buffer and set forward & active accordingly
        pos = self.absolute_pos
        if self.buffer1 and self.buffer1_start <= pos < self.buffer1_start + (len(self.buffer1) - 1):
            self.active = 1
            self.forward = pos - self.buffer1_start
        elif self.buffer2 and self.buffer2_start <= pos < self.buffer2_start + (len(self.buffer2) - 1):
            self.active = 2
            self.forward = pos - self.buffer2_start
        else:
            # out-of-range: we can't unget across buffers not present; clamp
            self.forward = max(0, self.forward - 1)

    # -----------------------------
    # Get lexeme string from lexemeBegin to current absolute_pos
    # (public API: string getLexeme())
    # -----------------------------
    def getLexeme(self) -> str:
        chars = []
        for pos in range(self.lexemeBegin, self.absolute_pos):
            ch = self._char_at(pos)
            if ch is not None:
                chars.append(ch)
        return ''.join(chars)

    # -----------------------------
    # Reset lexeme start (public API)
    # -----------------------------
    def resetLexemeBegin(self):
        self.lexemeBegin = self.absolute_pos

    # -----------------------------
    # Helper: get character at absolute position if in current buffers
    # -----------------------------
    def _char_at(self, pos: int) -> Optional[str]:
        if self.buffer1 and self.buffer1_start <= pos < self.buffer1_start + (len(self.buffer1) - 1):
            return self.buffer1[pos - self.buffer1_start]
        if self.buffer2 and self.buffer2_start <= pos < self.buffer2_start + (len(self.buffer2) - 1):
            return self.buffer2[pos - self.buffer2_start]
        return None

    # -----------------------------
    # Close file handle
    # -----------------------------
    def close(self):
        try:
            self.file.close()
        except Exception:
            pass


class SingleBufferStream:
    """Simple single-buffer implementation to compare performance."""
    def __init__(self, filename: str, buffer_size: int = 4096):
        self.filename = filename
        self.file = open(filename, "r", encoding="utf-8", errors="ignore")
        self.buffer_size = buffer_size
        self.buffer = []
        self.start = 0
        self.forward = 0
        self.file_offset = 0
        self.eof = False
        self.fill_durations = []
        self.total_read = 0
        self._fill()

    def _fill(self):
        start_time = time.perf_counter()
        start = self.file_offset
        data = self.file.read(self.buffer_size)
        data_len = len(data)
        self.buffer = list(data)
        self.buffer.append(SENTINEL)
        self.file_offset += data_len
        if data == "":
            self.eof = True
        duration = (time.perf_counter() - start_time) * 1000.0
        self.fill_durations.append(duration)

    def getNextChar(self):
        if self.forward >= len(self.buffer):
            return None
        ch = self.buffer[self.forward]
        if ch is SENTINEL:
            if self.eof:
                return None
            self._fill()
            self.forward = 0
            return self.getNextChar()
        self.forward += 1
        self.total_read += 1
        return ch

    def close(self):
        try:
            self.file.close()
        except Exception:
            pass


def benchmark(filename: str, buffer_size: int = 4096):
    # Run single-buffer and double-buffer reading and collect metrics
    # Single-buffer
    sb = SingleBufferStream(filename, buffer_size=buffer_size)
    t0 = time.perf_counter()
    count = 0
    while True:
        ch = sb.getNextChar()
        if ch is None:
            break
        count += 1
    t1 = time.perf_counter()
    single_time_ms = (t1 - t0) * 1000.0
    single_fill_avg = sum(sb.fill_durations) / len(sb.fill_durations) if sb.fill_durations else 0
    sb.close()

    # Double-buffer
    db = CharStream(filename, buffer_size=buffer_size)
    t0 = time.perf_counter()
    count_db = 0
    while True:
        ch = db.getNextChar()
        if ch is None:
            break
        count_db += 1
    t1 = time.perf_counter()
    double_time_ms = (t1 - t0) * 1000.0
    double_fill_avg = sum(db.fill_durations) / len(db.fill_durations) if db.fill_durations else 0

    # Build results
    results = {
        'buffer_size': buffer_size,
        'total_file_size': db.total_file_size if db.total_file_size >= 0 else count_db,
        'filename': filename,
        'chars_processed': count_db,
        'single_time_ms': single_time_ms,
        'double_time_ms': double_time_ms,
        'single_fill_avg_ms': single_fill_avg,
        'double_fill_avg_ms': double_fill_avg,
        'buffer_switches': db.switch_count,
        'transitions': db.transitions,
    }

    db.close()
    return results


def print_report(results):
    # Header
    print("Task 3: Character Stream Interface")
    print()
    print("Buffer Configuration:")
    print(f"- Buffer Size: {results['buffer_size']} bytes")
    print(f"- Total File Size: {results['total_file_size']} bytes")
    print()
    improvement = 0.0
    try:
        improvement = (results['single_time_ms'] - results['double_time_ms']) / results['single_time_ms'] * 100.0
    except Exception:
        improvement = 0.0

    print("Reading Statistics:")
    print(f"- Total buffer switches: {results['buffer_switches']}")
    print(f"- Average fill time: {results['double_fill_avg_ms']:.3f}ms")
    print(f"- Processing time (single buffer): {results['single_time_ms']:.3f}ms")
    print(f"- Processing time (double buffer): {results['double_time_ms']:.3f}ms")
    print(f"- Performance improvement: {improvement:.1f}%")
    print()
    print("Buffer Transition Demo:")
    if not results['transitions']:
        print("No buffer transitions recorded.")
    else:
        for i, t in enumerate(results['transitions'][:8]):
            old_act = t['old_active']
            new_act = t['new_active']
            pos = t['switch_at_absolute']
            old_tail = "".join(t['old_tail'])
            new_head = "".join(t['new_head'])
            old_display = " ".join(f"'{c}'" for c in old_tail)
            new_display = " ".join(f"'{c}'" for c in new_head)
            print(f"[Buffer {old_act} active] Position {max(0, pos - len(old_tail))}: {old_display}")
            print(f"[Buffer switch at position {pos}]")
            print(f"[Buffer {new_act} active] Position 0: {new_display}")
            print("...")

    print()
    print(f"Characters processed: {results['chars_processed']}")
    print("EOF reached successfully.")

    print()
    print("Tokens (sample from file, first 40 tokens):")
    try:
        fname = results.get('filename', None)
        if fname and os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            toks = tokenize_expression(content)
            sample = toks[:40]
            print(sample)
        else:
            print("Input file not available to tokenize.")
    except Exception as e:
        print("Tokenization failed:", e)


def main():
    filename = "tasksampel.cpp"
    if not os.path.exists(filename):
        print("Input file not found:", filename)
        return
    results = benchmark(filename, buffer_size=4096)
    print_report(results)


if __name__ == "__main__":
    main()
