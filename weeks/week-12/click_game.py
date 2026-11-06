"""Click the target. Run with python3 click_game.py or py click_game.py."""
import random
import tkinter as tk
from click_model import hit, tick_state

DURATION = 20
score = 0
seconds_left = 0
timer = None


def refresh():
    status.config(text=f"Score: {score}   Time: {seconds_left}")


def move_target():
    target.place(x=random.randint(30, 380), y=random.randint(90, 260))


def on_hit():
    global score
    if seconds_left <= 0:
        return
    score = hit(score, seconds_left)
    refresh()
    move_target()


def tick():
    global seconds_left, timer
    seconds_left = tick_state(seconds_left)
    refresh()
    if seconds_left > 0:
        timer = root.after(1000, tick)
    else:
        timer = None
        target.place_forget()


def start():
    global score, seconds_left, timer
    if timer is not None:
        root.after_cancel(timer)
    score = 0
    seconds_left = DURATION
    refresh()
    move_target()
    timer = root.after(1000, tick)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("One click, one function")
    root.geometry("500x360")
    status = tk.Label(root, text="Press Start", font=("Arial", 18))
    status.pack(pady=12)
    target = tk.Button(root, text="●", font=("Arial", 20), command=on_hit)
    tk.Button(root, text="Start / Restart", command=start).pack(side="bottom", pady=15)
    root.mainloop()
