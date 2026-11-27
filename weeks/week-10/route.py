from time import sleep


# 停留所のリストと、今いる停留所の番号を受け取る
def route_frame(stops, current):
    rows = ["CAMPUS SHUTTLE"]
    for i in range(len(stops)):
        marker = "  "
        if i == current:
            marker = "> "
        rows.append(marker + stops[i])
    return "\n".join(rows)


stops = ["Campus", "Library", "Station"]

# 描き直すたびに、次の停留所へ
for current in range(len(stops)):
    print("\033[2J\033[H" + route_frame(stops, current), flush=True)
    sleep(0.65)
