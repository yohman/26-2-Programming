from time import sleep

sky = [
    "  *                    .   ",
    "        .                * ",
    " *                 .       ",
    "          .                ",
    "    .                   *  ",
    "                     .     ",
    "  .                        ",
    "        .               .  ",
    "                           ",
    "                           ",
    "                           ",
]
rocket = [" /\\ ", " |^|", " /_\\", " /V\\"]
x = 12


def flight_frame(top, message):
    title = message.center(len(sky[0]))
    rows = [title.rstrip()]
    for y in range(len(sky)):
        line = sky[y]
        # ロケットの先端から何行下か
        part = y - top
        if 0 <= part < len(rocket):
            piece = rocket[part]
            end = x + len(piece)
            line = line[:x] + piece + line[end:]
        rows.append(line.rstrip())
    rows.append("-------- LAUNCH PAD -------")
    return "\n".join(rows)


for step in range(10):
    # 上に行くほど、先端の行番号は小さい
    top = max(0, 7 - step)
    if step == 0:
        message = "READY"
    elif top == 0:
        message = "ORBIT REACHED"
    else:
        message = "LIFTOFF"
    print("\033[2J\033[H" + flight_frame(top, message), flush=True)
    sleep(0.35)
