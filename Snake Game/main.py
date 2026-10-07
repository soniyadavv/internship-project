import random
import tkinter as tk

CELL = 24
COLS = 24
ROWS = 20
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
START_DELAY = 140
MIN_DELAY = 60

BG = "#1e2430"
TILE_A = "#263042"
TILE_B = "#222b3b"
SNAKE = "#4ade80"
HEAD = "#22c55e"
EYE = "#0b1f12"
FOOD = "#ef4444"
TEXT = "#e8eaf0"
MUTED = "#9aa3b5"
FONT = "Segoe UI"

DIRECTIONS = {
    "up": (0, -1), "w": (0, -1),
    "down": (0, 1), "s": (0, 1),
    "left": (-1, 0), "a": (-1, 0),
    "right": (1, 0), "d": (1, 0),
}


class SnakeGame:
    def __init__(self, root):
        self.root = root
        root.title("Snake Game")
        root.configure(bg=BG)
        root.resizable(False, False)

        self.high_score = 0

        tk.Label(root, text="SNAKE", font=(FONT, 22, "bold"), bg=BG, fg=TEXT).pack(pady=(14, 2))
        self.score_label = tk.Label(root, text="", font=(FONT, 13), bg=BG, fg=MUTED)
        self.score_label.pack(pady=(0, 8))

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=16)
        self.draw_background()

        tk.Label(root, text="Arrows / WASD to move     P pause     R restart",
                 font=(FONT, 10), bg=BG, fg=MUTED).pack(pady=(8, 14))

        root.bind("<Key>", self.on_key)
        self.reset()
        self.tick()

    def draw_background(self):
        for x in range(COLS):
            for y in range(ROWS):
                color = TILE_A if (x + y) % 2 == 0 else TILE_B
                self.canvas.create_rectangle(
                    x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL,
                    fill=color, outline="", tags="bg")

    def reset(self):
        start_x, start_y = COLS // 2, ROWS // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.queue = []
        self.eaten = 0
        self.state = "ready"
        self.place_food()
        self.update_score()
        self.draw()

    def place_food(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in self.snake]
        self.food = random.choice(free) if free else None

    def score(self):
        return self.eaten * 10

    def delay(self):
        return max(MIN_DELAY, START_DELAY - self.eaten * 4)

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score()}     Best: {self.high_score}")

    def on_key(self, event):
        key = event.keysym.lower()
        if key == "r":
            self.reset()
            return
        if key in ("space", "return") and self.state in ("over", "won"):
            self.reset()
            return
        if key == "p":
            if self.state == "running":
                self.state = "paused"
            elif self.state == "paused":
                self.state = "running"
            self.draw()
            return
        if key in DIRECTIONS and self.state in ("ready", "running"):
            new = DIRECTIONS[key]
            last = self.queue[-1] if self.queue else self.direction
            if new != last and (new[0] + last[0], new[1] + last[1]) != (0, 0):
                if len(self.queue) < 2:
                    self.queue.append(new)
            if self.state == "ready":
                self.state = "running"

    def tick(self):
        if self.state == "running":
            self.step()
        self.root.after(self.delay(), self.tick)

    def end_game(self, state):
        self.state = state
        self.high_score = max(self.high_score, self.score())
        self.update_score()

    def step(self):
        if self.queue:
            self.direction = self.queue.pop(0)
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        head = (head_x + dx, head_y + dy)
        eating = head == self.food
        body = self.snake if eating else self.snake[:-1]

        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in body:
            self.end_game("over")
            self.draw()
            return

        self.snake.insert(0, head)
        if eating:
            self.eaten += 1
            self.place_food()
            if self.food is None:
                self.end_game("won")
        else:
            self.snake.pop()
        self.update_score()
        self.draw()

    def draw(self):
        canvas = self.canvas
        canvas.delete("dyn")

        if self.food:
            fx, fy = self.food
            canvas.create_oval(fx * CELL + 4, fy * CELL + 4, (fx + 1) * CELL - 4, (fy + 1) * CELL - 4,
                               fill=FOOD, outline="", tags="dyn")

        for index, (x, y) in enumerate(self.snake):
            color = HEAD if index == 0 else SNAKE
            canvas.create_rectangle(x * CELL + 2, y * CELL + 2, (x + 1) * CELL - 2, (y + 1) * CELL - 2,
                                    fill=color, outline="", tags="dyn")

        head_x, head_y = self.snake[0]
        cx, cy = head_x * CELL + CELL // 2, head_y * CELL + CELL // 2
        dx, dy = self.direction
        if dx:
            eyes = [(cx + dx * 5, cy - 5), (cx + dx * 5, cy + 5)]
        else:
            eyes = [(cx - 5, cy + dy * 5), (cx + 5, cy + dy * 5)]
        for ex, ey in eyes:
            canvas.create_oval(ex - 2.5, ey - 2.5, ex + 2.5, ey + 2.5, fill=EYE, outline="", tags="dyn")

        messages = {
            "ready": "Press an arrow key or WASD to start",
            "paused": "Paused - press P to resume",
            "over": f"Game Over\nScore: {self.score()}\nPress Space to play again",
            "won": f"You filled the board!\nScore: {self.score()}\nPress Space to play again",
        }
        if self.state in messages:
            canvas.create_rectangle(WIDTH // 2 - 200, HEIGHT // 2 - 60, WIDTH // 2 + 200, HEIGHT // 2 + 60,
                                    fill="#11151d", outline="", tags="dyn")
            canvas.create_text(WIDTH // 2, HEIGHT // 2, text=messages[self.state], fill=TEXT,
                               font=(FONT, 15, "bold"), justify="center", tags="dyn")


def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()