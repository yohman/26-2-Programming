from time import sleep

# ドットの前の空白を1つずつ増やして、右へ動かす
for position in range(12):
    frame = " " * position + "."
    print("\r" + frame, end="", flush=True)
    sleep(0.2)

print()
