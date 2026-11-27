from time import sleep

lights = ["STOP", "GO", "WAIT"]


def signal_frame(active):
    rows = ["+----------+"]
    for light in lights:
        # 今の状態にだけ星印をつける
        mark = "*" if light == active else "."
        rows.append(f"| ({mark}) {light:<4} |")
    rows.append("+----------+")
    return "\n".join(rows)


for active in ["STOP", "GO", "WAIT", "STOP"]:
    print("\033[2J\033[H" + signal_frame(active), flush=True)
    sleep(0.65)
