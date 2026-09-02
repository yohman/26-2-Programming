# coding:utf-8
import tkinter as tk
import random
import math
import time

# ゲームウィンドウを初期化
root = tk.Tk()
root.geometry("500x400")  # ウィンドウサイズ
root.title("Shoot the Mad Spaceship!")

# ゲームの状態を表すグローバル変数
game_running = False
cannon_angle = 0  # 大砲の角度（度単位）
start_time = None
balls = []  # ボールを追跡するリスト
spaceship_interval = random.randint(1000, 3000)  # 宇宙船が再出現するランダムな間隔

# 宇宙船をランダムな間隔で再配置する関数
def move_spaceship():
    if not game_running:
        return
    x = random.randint(0, 450)
    y = random.randint(0, 350)
    canvas.coords(spaceship, x, y, x + 50, y + 50)
    root.after(random.randint(1000, 3000), move_spaceship)  # ランダムな間隔で再度呼び出す

# 大砲を回転させる関数
def rotate_cannon(event):
    global cannon_angle
    if not game_running:
        return
    if event.keysym == "Left":
        cannon_angle = (cannon_angle + 10) % 360  # 時計回りの回転
    elif event.keysym == "Right":
        cannon_angle = (cannon_angle - 10) % 360  # 反時計回りの回転
    update_cannon()

# 大砲の位置を更新する関数
def update_cannon():
    angle_radians = math.radians(cannon_angle)
    x1 = 250 + math.cos(angle_radians) * 50
    y1 = 300 - math.sin(angle_radians) * 50
    canvas.coords(cannon, 250, 300, x1, y1)

def start_game():
    global game_running, start_time, balls, spaceship
    game_running = True
    start_time = time.time()
    balls = []  # 以前の弾丸をクリア
    result_label.config(text="")
    start_button.place_forget()
    play_again_button.place_forget()

    # 既存の宇宙船を削除
    canvas.delete("spaceship")

    # ランダムな場所に新しい宇宙船を作成
    x = random.randint(0, 450)
    y = random.randint(0, 350)
    spaceship = canvas.create_rectangle(x, y, x + 50, y + 50, fill="red", outline="black", tags="spaceship")

    # 以前の弾丸を削除
    for item in canvas.find_withtag("bullet"):
        canvas.delete(item)

    move_spaceship()
    update_timer()

def shoot_ball():
    if not game_running:
        return
    angle_radians = math.radians(cannon_angle)
    ball_x = 250 + math.cos(angle_radians) * 50
    ball_y = 300 - math.sin(angle_radians) * 50
    ball_dx = math.cos(angle_radians) * 10
    ball_dy = -math.sin(angle_radians) * 10
    ball = {"id": canvas.create_oval(ball_x-5, ball_y-5, ball_x+5, ball_y+5, fill="black", tags="bullet"),
            "dx": ball_dx, "dy": ball_dy}
    balls.append(ball)
    move_balls()

# ボールを移動させ、衝突をチェックする関数
def move_balls():
    if not game_running:
        return
    global balls
    updated_balls = []
    for ball in balls:
        canvas.move(ball["id"], ball["dx"], ball["dy"])
        x1, y1, x2, y2 = canvas.coords(ball["id"])
        if x1 < 0 or x2 > 500 or y1 < 0 or y2 > 400:  # ボールが境界外に出たかどうかをチェック
            canvas.delete(ball["id"])
        else:
            updated_balls.append(ball)
            check_collision(x1, y1)
    balls = updated_balls
    if game_running:
        root.after(30, move_balls)

# ボールが宇宙船に当たったかどうかをチェックする関数
def check_collision(ball_x, ball_y):
    global game_running
    spaceship_coords = canvas.coords(spaceship)
    spaceship_x1, spaceship_y1, spaceship_x2, spaceship_y2 = spaceship_coords
    if spaceship_x1 < ball_x < spaceship_x2 and spaceship_y1 < ball_y < spaceship_y2:
        game_running = False
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)
        result_label.config(text=f"ゲームオーバー！所要時間: {elapsed_time} 秒", fg="green")
        canvas.delete(spaceship)
        play_again_button.place(x=200, y=200)

# タイマー表示を更新する関数
def update_timer():
    if game_running:
        elapsed_time = round(time.time() - start_time, 2)
        timer_label.config(text=f"時間: {elapsed_time} 秒")
        root.after(100, update_timer)

# ゲーム用のキャンバスを作成
canvas = tk.Canvas(root, width=500, height=400, bg="white")
canvas.pack()

# ラベルを作成
timer_label = tk.Label(root, text="時間: 0 秒", font=("Helvetica", 14))
timer_label.place(x=10, y=10)

result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.place(x=10, y=40)

# ボタンを作成
start_button = tk.Button(root, text="スタート", font=("Helvetica", 14), command=start_game)
start_button.place(x=200, y=200)

play_again_button = tk.Button(root, text="もう一度", font=("Helvetica", 14), command=start_game)

# 怒っているような長方形の宇宙船を作成
# spaceship = canvas.create_rectangle(0, 0, 50, 50, fill="red", outline="black")

# 大砲を作成
cannon = canvas.create_line(250, 300, 300, 250, width=5, fill="blue")

# 大砲の回転と発射をバインド
root.bind("<Left>", rotate_cannon)
root.bind("<Right>", rotate_cannon)
root.bind("<space>", lambda event: shoot_ball())

root.mainloop()
