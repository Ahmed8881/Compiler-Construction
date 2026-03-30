from common import *
from approach3_transition_table import _drive, T, N, ERR


class CompressedTable_Lexer(BaseLexer):
    _sparse = {(s, c): T[s][c]
               for s in range(len(T)) for c in range(N)
               if T[s][c] != ERR}

    def next_token(self):
        return _drive(self, lambda s, c: self._sparse.get((s, c), ERR))

    @classmethod
    def stats(cls):
        total  = len(T) * N
        stored = len(cls._sparse)
        print(f"  Full table : {total} cells  |  "
              f"Stored: {stored}  |  "
              f"Saved: {(1-stored/total)*100:.0f}%\n")


if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(CompressedTable_Lexer(src).tokenize_all(), "Compressed Table — Standalone")
    CompressedTable_Lexer.stats()
