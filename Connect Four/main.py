import tkinter as tk

ROWS = 6
COLS = 7
CELL = 88
HEADER = CELL
WIDTH = COLS * CELL
HEIGHT = HEADER + ROWS * CELL
RADIUS = CELL // 2 - 8
AI_DEPTH = 4
CENTER_ORDER = (3, 2, 4, 1, 5, 0, 6)

BG = "#1e2430"
BOARD = "#2457d6"
PANEL = "#2a3140"
TEXT = "#e8eaf0"
MUTED = "#9aa3b5"
FONT = "Segoe UI"
COLORS = {1: "#ef4444", 2: "#facc15"}
EDGES = {1: "#b91c1c", 2: "#ca8a04"}


def build_windows():
    windows = []
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                end_r, end_c = r + 3 * dr, c + 3 * dc
                if 0 <= end_r < ROWS and 0 <= end_c < COLS:
                    windows.append([(r + i * dr, c + i * dc) for i in range(4)])
    return windows


WINDOWS = build_windows()


def drop_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            return r
    return None


def valid_columns(board):
    return [c for c in CENTER_ORDER if board[0][c] == 0]


def find_four(board):
    for window in WINDOWS:
        first = board[window[0][0]][window[0][1]]
        if first and all(board[r][c] == first for r, c in window):
            return first, window
    return None


def has_four(board, player):
    for window in WINDOWS:
        if all(board[r][c] == player for r, c in window):
            return True
    return False


def evaluate(board, ai, human):
    score = sum(1 for r in range(ROWS) if board[r][3] == ai) * 3
    for window in WINDOWS:
        values = [board[r][c] for r, c in window]
        mine = values.count(ai)
        theirs = values.count(human)
        empty = values.count(0)
        if mine == 3 and empty == 1:
            score += 5
        elif mine == 2 and empty == 2:
            score += 2
        if theirs == 3 and empty == 1:
            score -= 4
    return score


def minimax(board, depth, alpha, beta, maximizing, ai, human):
    if has_four(board, ai):
        return None, 1000000 + depth
    if has_four(board, human):
        return None, -1000000 - depth
    moves = valid_columns(board)
    if not moves:
        return None, 0
    if depth == 0:
        return None, evaluate(board, ai, human)

    best_col = moves[0]
    if maximizing:
        best = -10 ** 9
        for col in moves:
            row = drop_row(board, col)
            board[row][col] = ai
            _, score = minimax(board, depth - 1, alpha, beta, False, ai, human)
            board[row][col] = 0
            if score > best:
                best, best_col = score, col
            alpha = max(alpha, best)
            if alpha >= beta:
                break
    else:
        best = 10 ** 9
        for col in moves:
            row = drop_row(board, col)
            board[row][col] = human
            _, score = minimax(board, depth - 1, alpha, beta, True, ai, human)
            board[row][col] = 0
            if score < best:
                best, best_col = score, col
            beta = min(beta, best)
            if alpha >= beta:
                break
    return best_col, best


def choose_ai_move(board, ai, human):
    moves = valid_columns(board)
    for player in (ai, human):
        for col in moves:
            row = drop_row(board, col)
            board[row][col] = player
            wins = has_four(board, player)
            board[row][col] = 0
            if wins:
                return col
    col, _ = minimax(board, AI_DEPTH, -10 ** 9, 10 ** 9, True, ai, human)
    return col


class ConnectFour:
    def __init__(self, root):
        self.root = root
        root.title("Connect Four")
        root.configure(bg=BG)
        root.resizable(False, False)

        self.vs_computer = True
        self.scores = {1: 0, 2: 0, 0: 0}
        self.generation = 0
        self.hover_col = None

        tk.Label(root, text="CONNECT FOUR", font=(FONT, 22, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(14, 2))
        self.status = tk.Label(root, text="", font=(FONT, 14), bg=BG, fg=MUTED)
        self.status.pack(pady=(0, 8))

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG,
                                highlightthickness=0, cursor="hand2")
        self.canvas.pack(padx=16)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)

        self.score_label = tk.Label(root, text="", font=(FONT, 12), bg=BG, fg=TEXT)
        self.score_label.pack(pady=(10, 6))

        controls = tk.Frame(root, bg=BG)
        controls.pack(pady=(0, 14))
        self.mode_button = tk.Button(
            controls, text="", font=(FONT, 11), bg=PANEL, fg=TEXT,
            activebackground="#343d50", activeforeground=TEXT,
            relief="flat", padx=12, pady=6, command=self.toggle_mode)
        self.mode_button.pack(side="left", padx=6)
        tk.Button(
            controls, text="New Game", font=(FONT, 11), bg=PANEL, fg=TEXT,
            activebackground="#343d50", activeforeground=TEXT,
            relief="flat", padx=12, pady=6, command=self.reset).pack(side="left", padx=6)

        self.reset()

    def player_name(self, player):
        if self.vs_computer:
            return "You (Red)" if player == 1 else "Computer (Yellow)"
        return "Red" if player == 1 else "Yellow"

    def turn_text(self, player):
        if self.vs_computer:
            return "Your turn" if player == 1 else "Computer is thinking..."
        return f"{self.player_name(player)}'s turn"

    def win_text(self, player):
        if self.vs_computer:
            return "You win!" if player == 1 else "Computer wins!"
        return f"{self.player_name(player)} wins!"

    def human_turn(self):
        return not (self.vs_computer and self.turn == 2)

    def update_labels(self):
        self.score_label.config(
            text=f"{self.player_name(1)}: {self.scores[1]}     Draws: {self.scores[0]}     "
                 f"{self.player_name(2)}: {self.scores[2]}")
        self.mode_button.config(
            text="Mode: vs Computer" if self.vs_computer else "Mode: 2 Players")

    def reset(self):
        self.generation += 1
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.turn = 1
        self.over = False
        self.busy = False
        self.win_cells = []
        self.status.config(text=self.turn_text(1))
        self.update_labels()
        self.render()

    def toggle_mode(self):
        self.vs_computer = not self.vs_computer
        self.scores = {1: 0, 2: 0, 0: 0}
        self.reset()

    def disc(self, x, y, player):
        self.canvas.create_oval(x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS,
                                fill=COLORS[player], outline=EDGES[player], width=3)

    def render(self, falling=None):
        canvas = self.canvas
        canvas.delete("all")
        if (self.hover_col is not None and not self.over and not self.busy
                and self.human_turn()):
            self.disc(self.hover_col * CELL + CELL // 2, HEADER // 2, self.turn)
        canvas.create_rectangle(0, HEADER, WIDTH, HEIGHT, fill=BOARD, outline="")
        for r in range(ROWS):
            for c in range(COLS):
                x = c * CELL + CELL // 2
                y = HEADER + r * CELL + CELL // 2
                value = self.board[r][c]
                if value:
                    self.disc(x, y, value)
                else:
                    canvas.create_oval(x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS,
                                       fill=BG, outline="#1a44a8", width=3)
        if falling:
            col, y, player = falling
            self.disc(col * CELL + CELL // 2, y, player)
        for r, c in self.win_cells:
            x = c * CELL + CELL // 2
            y = HEADER + r * CELL + CELL // 2
            canvas.create_oval(x - RADIUS + 6, y - RADIUS + 6, x + RADIUS - 6, y + RADIUS - 6,
                               outline="#ffffff", width=4)

    def on_motion(self, event):
        col = min(max(event.x // CELL, 0), COLS - 1)
        if col != self.hover_col:
            self.hover_col = col
            if not self.busy:
                self.render()

    def on_leave(self, event):
        self.hover_col = None
        if not self.busy:
            self.render()

    def on_click(self, event):
        if self.over or self.busy or not self.human_turn():
            return
        col = event.x // CELL
        if 0 <= col < COLS:
            self.drop(col)

    def drop(self, col):
        row = drop_row(self.board, col)
        if row is None:
            return
        self.busy = True
        self.animate(self.generation, col, row, self.turn, HEADER // 2, 4)

    def animate(self, generation, col, row, player, y, speed):
        if generation != self.generation:
            return
        target = HEADER + row * CELL + CELL // 2
        y = min(y + speed, target)
        self.render(falling=(col, y, player))
        if y >= target:
            self.land(generation, col, row, player)
        else:
            self.root.after(14, self.animate, generation, col, row, player, y, speed + 2)

    def land(self, generation, col, row, player):
        if generation != self.generation:
            return
        self.board[row][col] = player
        self.busy = False
        result = find_four(self.board)
        if result:
            winner, cells = result
            self.over = True
            self.win_cells = cells
            self.scores[winner] += 1
            self.status.config(text=self.win_text(winner))
        elif not valid_columns(self.board):
            self.over = True
            self.scores[0] += 1
            self.status.config(text="It's a draw!")
        else:
            self.turn = 3 - player
            self.status.config(text=self.turn_text(self.turn))
            if self.vs_computer and self.turn == 2:
                self.busy = True
                self.root.after(350, self.computer_move, generation)
        self.update_labels()
        self.render()

    def computer_move(self, generation):
        if generation != self.generation or self.over or self.turn != 2:
            return
        self.busy = False
        board_copy = [row[:] for row in self.board]
        self.drop(choose_ai_move(board_copy, 2, 1))


def main():
    root = tk.Tk()
    ConnectFour(root)
    root.mainloop()


if __name__ == "__main__":
    main()