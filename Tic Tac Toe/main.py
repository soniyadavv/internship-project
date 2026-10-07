import random
import tkinter as tk

LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)

BG = "#1e2430"
PANEL = "#2a3140"
WIN_BG = "#3f5a46"
X_COLOR = "#ff6b6b"
O_COLOR = "#4dd0e1"
TEXT = "#e8eaf0"
MUTED = "#9aa3b5"
FONT = "Segoe UI"


def find_winner(board):
    for a, b, c in LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None, None


def minimax(board, player, ai, human):
    mark, _ = find_winner(board)
    if mark == ai:
        return 1
    if mark == human:
        return -1
    if all(board):
        return 0
    scores = []
    for i in range(9):
        if not board[i]:
            board[i] = player
            scores.append(minimax(board, human if player == ai else ai, ai, human))
            board[i] = ""
    return max(scores) if player == ai else min(scores)


def best_move(board, ai, human):
    if not any(board):
        return random.choice([0, 2, 4, 6, 8])
    best_score = -2
    moves = []
    for i in range(9):
        if not board[i]:
            board[i] = ai
            score = minimax(board, human, ai, human)
            board[i] = ""
            if score > best_score:
                best_score = score
                moves = [i]
            elif score == best_score:
                moves.append(i)
    return random.choice(moves)


class TicTacToe:
    def __init__(self, root):
        self.root = root
        root.title("Tic Tac Toe")
        root.configure(bg=BG)
        root.resizable(False, False)

        self.vs_computer = True
        self.scores = {"X": 0, "O": 0, "D": 0}
        self.board = [""] * 9
        self.turn = "X"
        self.over = False

        tk.Label(root, text="TIC TAC TOE", font=(FONT, 22, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(16, 2))
        self.status = tk.Label(root, text="", font=(FONT, 14), bg=BG, fg=MUTED)
        self.status.pack(pady=(0, 10))

        grid = tk.Frame(root, bg=BG)
        grid.pack(padx=24)
        self.cells = []
        for i in range(9):
            button = tk.Button(
                grid, text="", font=(FONT, 40, "bold"), width=2, height=1,
                bg=PANEL, fg=TEXT, activebackground="#343d50",
                relief="flat", bd=0, cursor="hand2",
                command=lambda i=i: self.play(i))
            button.grid(row=i // 3, column=i % 3, padx=4, pady=4)
            self.cells.append(button)

        self.score_label = tk.Label(root, text="", font=(FONT, 12), bg=BG, fg=TEXT)
        self.score_label.pack(pady=(12, 6))

        controls = tk.Frame(root, bg=BG)
        controls.pack(pady=(0, 16))
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

    def turn_text(self, mark):
        if self.vs_computer:
            return "Your turn" if mark == "X" else "Computer is thinking..."
        return f"Player {mark}'s turn"

    def win_text(self, mark):
        if self.vs_computer:
            return "You win!" if mark == "X" else "Computer wins!"
        return f"Player {mark} wins!"

    def update_scores(self):
        left = "You (X)" if self.vs_computer else "Player X"
        right = "Computer (O)" if self.vs_computer else "Player O"
        self.score_label.config(
            text=f"{left}: {self.scores['X']}     Draws: {self.scores['D']}     "
                 f"{right}: {self.scores['O']}")
        self.mode_button.config(
            text="Mode: vs Computer" if self.vs_computer else "Mode: 2 Players")

    def reset(self):
        self.board = [""] * 9
        self.turn = "X"
        self.over = False
        for button in self.cells:
            button.config(text="", bg=PANEL)
        self.status.config(text=self.turn_text("X"))
        self.update_scores()

    def toggle_mode(self):
        self.vs_computer = not self.vs_computer
        self.scores = {"X": 0, "O": 0, "D": 0}
        self.reset()

    def play(self, i):
        if self.over or self.board[i]:
            return
        if self.vs_computer and self.turn == "O":
            return
        self.place(i)
        if not self.over and self.vs_computer and self.turn == "O":
            self.root.after(350, self.computer_move)

    def computer_move(self):
        if self.over or self.turn != "O" or not self.vs_computer:
            return
        self.place(best_move(self.board, "O", "X"))

    def place(self, i):
        mark = self.turn
        self.board[i] = mark
        self.cells[i].config(text=mark, fg=X_COLOR if mark == "X" else O_COLOR)
        winner, line = find_winner(self.board)
        if winner:
            self.over = True
            self.scores[winner] += 1
            for j in line:
                self.cells[j].config(bg=WIN_BG)
            self.status.config(text=self.win_text(winner))
        elif all(self.board):
            self.over = True
            self.scores["D"] += 1
            self.status.config(text="It's a draw!")
        else:
            self.turn = "O" if mark == "X" else "X"
            self.status.config(text=self.turn_text(self.turn))
        self.update_scores()


def main():
    root = tk.Tk()
    TicTacToe(root)
    root.mainloop()


if __name__ == "__main__":
    main()