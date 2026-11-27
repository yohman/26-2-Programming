from time import sleep

# 固定の屋根に、雨の行を2行足す
def rain_frame(drops):
    return (
        drops + "\n" + "  " + drops + "\n"
        "        /\\\n"
        "    ___/  \\___\n"
        "      | [] |\n"
        "______|____|______"
    )


# 雨の模様を順番に切り替える
rain = [" .   .    .  .", "  /   /  /   /", "   .   .  .   ."]
for repeat in range(3):
    for drops in rain:
        # 画面を消してから、次のコマを描く
        print("\033[2J\033[H" + rain_frame(drops), flush=True)
        sleep(0.28)
