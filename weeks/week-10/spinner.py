from time import sleep

symbols = ["|", "/", "-", "\\"]
for symbol in symbols * 3:
    print("\r" + symbol, end="", flush=True)
    sleep(0.2)

print()
