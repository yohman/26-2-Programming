from time import sleep

symbols = ["|", "/", "-", "\\"]

# 4つの記号を3周。1コマずつ同じ場所に上書きする
for symbol in symbols * 3:
    print("\r" + symbol, end="", flush=True)
    sleep(0.2)

print()
