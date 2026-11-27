from time import sleep

faces = ["🙂", "😮", "😄"]
for face in faces * 2:
    print("\r" + face, end="", flush=True)
    sleep(0.45)

print()
