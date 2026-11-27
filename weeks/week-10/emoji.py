from time import sleep

faces = ["🙂", "😮", "😄"]

# 同じ場所で表情を変える。リストの順に2周する
for face in faces * 2:
    print("\r" + face, end="", flush=True)
    sleep(0.45)

print()
