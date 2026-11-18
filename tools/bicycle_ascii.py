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
