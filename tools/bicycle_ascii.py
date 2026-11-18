"""ASCII bicycle art and optional, beginner-readable notebook examples."""
import html
import json

FRAMES = ["    __o\n  _ \\<_\n (-)/(-)", "    __o\n  _ \\<_\n (\\)/(\\)", "    __o\n  _ \\<_\n (|)/(|)", "    __o\n  _ \\<_\n (/)/(/)"]
STILL = r'''
# rはバックスラッシュをそのまま表示。三重引用符で複数行を書く
bike = r"""
    __o
  _ \<_
 (-)/(-)
"""
print(bike)'''.strip()
ANIMATION = r'''
# アニメーションの回数と速さを先に設定する
turns = 4
pause = 0.15
wheels = ["-", "\\", "|", "/"]

# Notebookの出力を入れ替える道具。pandasは不要
import time
from IPython.display import clear_output

# 4種類の車輪を順番に表示する。有限回なので自動で止まる
for spoke in wheels * turns:
    clear_output(wait=True)
    print(r"    __o")
    print(r"  _ \<_")
    print(f" ({spoke})/({spoke})")
    time.sleep(pause)'''.strip()


def art(kind='ride'):
    """No image asset: the visible bicycle consists entirely of ASCII text."""
    frames=html.escape(json.dumps(FRAMES),quote=True)
    return (f'<div class="ascii-scene ascii-{kind}" data-ascii-scene data-no-copy data-frames="{frames}">'
            '<div class="ascii-lane" role="img" aria-label="ASCII bicycle with spinning wheels">'
            '<pre data-ascii-bike aria-hidden="true">'+html.escape(FRAMES[0])+'</pre></div>'
            '<button type="button" class="ascii-toggle" data-ascii-toggle aria-pressed="false" aria-label="Play bicycle animation">▶</button></div>')


# Each weather symbol uses only ASCII characters. Colour belongs to the HTML.
WEATHER = {
    'sun': ('Sun', [
        " \\  |  / \n  .---.  \n--( o )--\n  '---'  \n /  |  \\ ",
        "    |    \n\\ .---. /\n -( o )- \n/ '---' \\\n    |    "
    ]),
    'rain': ('Rain', [
        "   .--.   \n _(    )_ \n(________)\n  / / /   \n / / /    ",
        "   .--.   \n _(    )_ \n(________)\n / / /    \n  / / /   "
    ]),
    'lightning': ('Lightning', [
        "   .--.   \n _(    )_ \n(________)\n    /_    \n     /    ",
        "   .--.   \n _(    )_ \n(________)\n     /_   \n      /   "
    ]),
    'snow': ('Snow', [
        "   .--.   \n _(    )_ \n(________)\n  * . *   \n . * .    ",
        "   .--.   \n _(    )_ \n(________)\n . * .    \n  * . *   "
    ])
}


def weather_art():
    symbols=''
    for kind,(label,frames) in WEATHER.items():
        frames=['\n'.join(line.rstrip() for line in frame.splitlines()) for frame in frames]
        encoded=html.escape(json.dumps(frames),quote=True)
        symbols += (f'<pre class="ascii-{kind}" data-ascii-weather-art data-ascii-frames="{encoded}" '
                    f'role="img" aria-label="ASCII {label.lower()}">'+html.escape(frames[0])+'</pre>')
    return ('<div class="ascii-scene ascii-weather" data-ascii-scene data-no-copy '
            'data-animation-label="weather animation" data-frame-ms="600">'
            '<div class="ascii-sky">'+symbols+'</div>'
            '<button type="button" class="ascii-toggle" data-ascii-toggle aria-pressed="false" aria-label="Play weather animation">▶</button></div>')
