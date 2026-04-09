# Connect 4 Solver

from collections import deque

"""
    Globals
"""
# typedef
Tile  = int # 0 | 1 | 2
Board = list[list[Tile]] # [7][6]Tile
Idx   = int # 0..7

# constexpr
ROWS = 6
COLS = 7


"""
    Helper functions
"""
def game_won(board: Board, sel_row: Idx, sel_col: Idx, turn: Tile) -> bool:
    horizontal = [board[sel_row][col] for col in range(COLS)]
    vertical   = [board[row][sel_col] for row in range(ROWS)]
    positive   = [board[row][col] for row in range(ROWS) for col in range(COLS)
                  if col + row == sel_col + sel_row]
    negative   = [board[row][col] for row in range(ROWS) for col in range(COLS)
                  if col + sel_row == row + sel_col]
    
    for arr in [horizontal, vertical, positive, negative]:
        ct = 0
        for item in arr:
            if item != turn:
                ct = 0
            elif ct == 3:
                return True
            else:
                ct += 1
    return False


def game_drawn(board: Board) -> bool:
    return all(board[0])  # All spots filled up, != 0


def find_row(board: Board, col: int) -> int:
    """ return index of first available row """
    ret = -1
    for r in range(ROWS):
        if board[r][col] == 0:
            ret = r
    return ret


"""
    SLOW PYTHON DFS
"""

MAX_EVALS = 137_257

def dfs(board: Board, turn: Tile, num_evals: list[int], depth: int = 0, tree_idx=1) -> tuple[Idx, int]:
    """ Idx: 0..6, Score: 0 | 1 | 2 """
    if len(num_evals) == depth:
        num_evals.append(0)
    num_evals[depth] += 1
    
    branches = sum(x == 0 for x in board[0])
    
    if branches == 0 or tree_idx*branches > MAX_EVALS:
        for col in [3, 4, 2, 5, 1, 6, 0]: #range(COLS):
            if find_row(board, col) != -1:
                return col, 0
        return -1, 0
    
    idx_draw  = -1
    idx_valid = -1
    score     =  3-turn  # Default to losing score
    
    # For each playable column
    #for col in range(COLS):
    for col in [3, 4, 2, 5, 1, 6, 0]:
        
        # Find row that puck drops to
        row = find_row(board, col)
        if row == -1:
            continue
        if idx_valid == -1: idx_valid = col
        
        # Play move and check for win/draw
        board[row][col] = turn
        if game_won(board, row, col, turn):
            board[row][col] = 0
            return (col, turn)
        if game_drawn(board):
            if idx_draw == -1: idx_draw = col
            score = 0
            board[row][col] = 0
            continue
        
        # No obvious game end, recurse DFS
        _, sc = dfs(board, 3-turn, num_evals, depth+1, tree_idx*branches)
        board[row][col] = 0
        
        # Winning move, stop branching
        if sc == turn:
            return (col, turn)
        # Drawing move, remember for later
        elif sc == 0:
            if idx_draw == -1: idx_draw = col
            score = 0
    
    return (idx_draw if idx_draw != -1 else idx_valid, score)


"""
    Blend opening LOOPUP table with DFS search
"""

LOOKUP: dict[int, int] = {0:3}

""" board[i][j] = 0 | 1 | 2 -> read board as trinary number in 0..3^42 """
def _hash(board: Board) -> int:
    ret: int = 0
    for row in board:
        for x in row:
            ret = 3*ret + x
    return ret

def smart_move(board: Board, turn: Tile) -> Idx:
    # Initial moves stored in hash table
    state = _hash(board)
    if state in LOOKUP:
        print(f"LOOKUP MOVE")
        return LOOKUP[state]
    mirror = [row[::-1] for row in board]
    m_state = _hash(mirror)
    if m_state in LOOKUP:
        print(f"LOOKUP MOVE")
        return 6 - LOOKUP[m_state]
    
    # After opening, use DFS to find best move
    num_evals = []
    mv, sc = dfs(board, turn, num_evals)
    print(f"DFS: {sum(num_evals):>6} states | depth={len(num_evals):<2} | {num_evals}")
    return mv


def demo():
    board = [[0] * 7 for _ in range(6)]
    turn = 2
    while True:
        turn = 3 - turn
        col, score = dfs(board, turn, depth=3)
        row = find_row(board, col)
        board[row][col] = turn
        
        for r in board:
            r = ' '.join(map(str, r)).replace('0', '.')
            r = r.replace('1', "\033[43m" + '1' + "\033[0m") # Yellow highlight
            r = r.replace('2', "\033[44m" + '2' + "\033[0m") # Blue highlight
            print(r)
        
        if game_won(board, row, col, turn):
            print(f"Player {turn} WINS")
            break
        if game_drawn(board):
            print("GAME DRAW")
            break
        print("\n\n")

if __name__ == "__main__":
    demo()
