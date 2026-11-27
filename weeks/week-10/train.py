from time import sleep

# 空白の数で、列車の位置を変える
def train_frame(position):
    return " " * position + "[==][==][__]>o"


# 1コマずつ同じ行に描き直す。steps はコマ数、delay は待ち時間（秒）
def animate_train(steps, delay):
    for position in range(steps):
        print("\r" + train_frame(position), end="", flush=True)
        sleep(delay)

    # 終わったら改行してターミナルの入力欄に戻る
    print()


animate_train(18, 0.12)
