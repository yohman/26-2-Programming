from time import sleep

spinner = ["|", "/", "-", "\\"]
faces = ["🙂", "😮"]


def tiny_frame(step):
    # % は余り。0〜3、0〜1を繰り返す
    spin = spinner[step % 4]
    face = faces[step % 2]
    dot = " " * step + "."
    return f"SPIN   {spin}\nDOT    {dot}\nEMOJI  {face}"


for step in range(12):
    print("\033[2J\033[H" + tiny_frame(step), flush=True)
    sleep(0.2)
