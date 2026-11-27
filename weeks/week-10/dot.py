from time import sleep

for position in range(12):
    frame = " " * position + "."
    print("\r" + frame, end="", flush=True)
    sleep(0.2)

print()
