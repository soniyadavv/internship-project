import time
import tkinter as tk
from datetime import datetime

BG = "#e6e7e8"
BEZEL = "#fafafa"
BEZEL_EDGE = "#d2d2d2"
LCD = "#d5d7d9"
INK = "#111111"
GHOST = "#c7c9cb"
DIVIDER = "#8a8c8e"

DIGITS = {
    "0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg",
    "5": "acdfg", "6": "acdefg", "7": "abc", "8": "abcdefg", "9": "abcdfg",
    " ": "",
}


def rounded_rect(canvas, x1, y1, x2, y2, r, **options):
    points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
              x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
              x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(points, smooth=True, **options)


def segment_points(x, y, w, h, t, name, skew):
    g = t * 0.12
    left, right = x + t / 2, x + w - t / 2
    top, mid, bottom = y + t / 2, y + h / 2, y + h - t / 2

    if name in "adg":
        cy = {"a": top, "g": mid, "d": bottom}[name]
        x0, x1 = left + g, right - g
        pts = [(x0, cy), (x0 + t / 2, cy - t / 2), (x1 - t / 2, cy - t / 2),
               (x1, cy), (x1 - t / 2, cy + t / 2), (x0 + t / 2, cy + t / 2)]
    else:
        cx = left if name in "ef" else right
        y0, y1 = (top + g, mid - g) if name in "bf" else (mid + g, bottom - g)
        pts = [(cx, y0), (cx + t / 2, y0 + t / 2), (cx + t / 2, y1 - t / 2),
               (cx, y1), (cx - t / 2, y1 - t / 2), (cx - t / 2, y0 + t / 2)]

    flat = []
    for px, py in pts:
        flat += [px + (y + h - py) * skew, py]
    return flat


def create_digit(canvas, x, y, w, h, t, skew=0.08):
    return {
        name: canvas.create_polygon(
            segment_points(x, y, w, h, t, name, skew), fill=GHOST, outline="")
        for name in "abcdefg"
    }


def set_digit(canvas, digit, char):
    lit = DIGITS.get(char, "")
    for name, item in digit.items():
        canvas.itemconfig(item, fill=INK if name in lit else GHOST)


def show_pair(canvas, digits, text):
    for digit, char in zip(digits, text):
        set_digit(canvas, digit, char)


def build_display(root):
    canvas = tk.Canvas(root, width=960, height=440, bg=BG, highlightthickness=0)
    canvas.pack()

    rounded_rect(canvas, 20, 30, 940, 410, 60, fill=BEZEL, outline=BEZEL_EDGE, width=2)
    canvas.create_rectangle(70, 80, 890, 360, fill=LCD, outline="#b9bbbd", width=2)

    ui = {}
    ui["am"] = canvas.create_text(95, 150, text="AM", anchor="w", fill=GHOST,
                                  font=("Arial", 18, "bold"))
    ui["pm"] = canvas.create_text(95, 290, text="PM", anchor="w", fill=GHOST,
                                  font=("Arial", 18, "bold"))

    ui["hour"] = [create_digit(canvas, 180, 110, 100, 200, 22),
                  create_digit(canvas, 300, 110, 100, 200, 22)]
    ui["minute"] = [create_digit(canvas, 470, 110, 100, 200, 22),
                    create_digit(canvas, 590, 110, 100, 200, 22)]
    ui["colon"] = [canvas.create_oval(425, 170, 445, 190, fill=GHOST, outline=""),
                   canvas.create_oval(425, 235, 445, 255, fill=GHOST, outline="")]

    label_font = ("Arial", 12, "bold")
    canvas.create_text(725, 112, text="SECONDS", anchor="w", font=label_font, fill=INK)
    ui["second"] = [create_digit(canvas, 760, 126, 32, 62, 8),
                    create_digit(canvas, 805, 126, 32, 62, 8)]
    canvas.create_line(725, 204, 875, 204, fill=DIVIDER)

    canvas.create_text(725, 220, text="MONTH", anchor="w", font=label_font, fill=INK)
    canvas.create_text(800, 220, text="DATE", anchor="w", font=label_font, fill=INK)
    ui["month"] = [create_digit(canvas, 725, 236, 28, 62, 8),
                   create_digit(canvas, 762, 236, 28, 62, 8)]
    ui["date"] = [create_digit(canvas, 815, 236, 28, 62, 8),
                  create_digit(canvas, 852, 236, 28, 62, 8)]
    canvas.create_line(725, 314, 875, 314, fill=DIVIDER)

    ui["weekday"] = canvas.create_text(725, 337, text="", anchor="w",
                                       font=("Arial", 16, "bold"), fill=INK)
    return canvas, ui


def update_clock(root, canvas, ui):
    now = datetime.now()

    hour = now.strftime("%I").lstrip("0").rjust(2)
    show_pair(canvas, ui["hour"], hour)
    show_pair(canvas, ui["minute"], now.strftime("%M"))
    show_pair(canvas, ui["second"], now.strftime("%S"))
    show_pair(canvas, ui["month"], now.strftime("%m"))
    show_pair(canvas, ui["date"], now.strftime("%d"))

    is_pm = now.strftime("%p") == "PM"
    canvas.itemconfig(ui["am"], fill=GHOST if is_pm else INK)
    canvas.itemconfig(ui["pm"], fill=INK if is_pm else GHOST)
    canvas.itemconfig(ui["weekday"], text=now.strftime("%A").upper())

    colon_colour = INK if now.second % 2 == 0 else GHOST
    for dot in ui["colon"]:
        canvas.itemconfig(dot, fill=colon_colour)

    delay_ms = int((1 - time.time() % 1) * 1000) + 5
    root.after(delay_ms, update_clock, root, canvas, ui)


def main():
    root = tk.Tk()
    root.title("Digital Clock")
    root.configure(bg=BG)
    root.resizable(False, False)

    canvas, ui = build_display(root)
    update_clock(root, canvas, ui)
    root.mainloop()


if __name__ == "__main__":
    main()