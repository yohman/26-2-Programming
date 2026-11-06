"""Optional extension of the course shooter. Arrow keys aim; Space fires.

Run with python3 stretch-shooter.py or py stretch-shooter.py.
One animation loop is scheduled per game, not once per projectile.
"""
import math
import random
import time
import tkinter as tk

WIDTH, HEIGHT = 500, 400
running = False
angle = 90
balls = []
timers = {}
started = 0


def inside(x, y, left, top, width, height):
    return left <= x <= left + width and top <= y <= top + height


def schedule(name, delay, callback):
    timers[name] = root.after(delay, callback)


def cancel_timers():
    for timer in timers.values():
        root.after_cancel(timer)
    timers.clear()


def draw_cannon():
    radians = math.radians(angle)
    canvas.coords(cannon, 250, 350,
                  250 + math.cos(radians) * 45,
                  350 - math.sin(radians) * 45)


def rotate(event):
    global angle
    angle = (angle + (10 if event.keysym == "Left" else -10)) % 360
    draw_cannon()


def move_target():
    if not running:
        return
    x, y = random.randint(20, 420), random.randint(50, 240)
    canvas.coords(target, x, y, x + 50, y + 35)
    schedule("target", random.randint(1000, 2500), move_target)


def shoot(event=None):
    if not running:
        return
    radians = math.radians(angle)
    x, y = 250 + math.cos(radians) * 45, 350 - math.sin(radians) * 45
    balls.append({"id": canvas.create_oval(x-4, y-4, x+4, y+4, fill="#315876"),
                  "dx": math.cos(radians)*8, "dy": -math.sin(radians)*8})
    # The animation is already running; do not start another timer here.


def animate():
    global running, balls
    if not running:
        return
    kept = []
    left, top, right, bottom = canvas.coords(target)
    for ball in balls:
        canvas.move(ball["id"], ball["dx"], ball["dy"])
        x1, y1, x2, y2 = canvas.coords(ball["id"])
        x, y = (x1+x2)/2, (y1+y2)/2
        if inside(x, y, left, top, right-left, bottom-top):
            running = False
        if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
            kept.append(ball)
        else:
            canvas.delete(ball["id"])
    balls = kept
    if running:
        status.config(text=f"Time: {time.monotonic()-started:.1f}s  ·  Space to shoot")
        schedule("animation", 30, animate)
    else:
        cancel_timers()
        status.config(text=f"Hit! {time.monotonic()-started:.1f}s · Start to play again")


def start():
    global running, started, balls
    cancel_timers()
    for ball in balls:
        canvas.delete(ball["id"])
    balls = []
    running, started = True, time.monotonic()
    move_target()
    animate()
    root.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Functions, loops, and a small shooter")
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#f6f5f0")
    canvas.pack()
    target = canvas.create_rectangle(40, 60, 90, 95, fill="#3f6d57")
    cannon = canvas.create_line(250, 350, 250, 305, width=5, fill="#315876")
    status = tk.Label(root, text="Left / Right: aim · Space: fire")
    status.pack()
    tk.Button(root, text="Start / Restart", command=start).pack(pady=8)
    root.bind("<Left>", rotate)
    root.bind("<Right>", rotate)
    root.bind("<space>", shoot)
    root.mainloop()
