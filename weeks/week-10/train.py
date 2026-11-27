from time import sleep

# 空白の数で、列車の位置を変える
def train_frame(position):
    return " " * position + "[==][==][__]>o"


# 1コマずつ同じ行に描き直す
for position in range(0, 18):
    print("\r" + train_frame(position), end="", flush=True)
    sleep(0.12)

# 最後に改行して、プロンプトと絵を分ける
print()
