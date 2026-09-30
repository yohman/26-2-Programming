# Tutorial 04 — `.venv`とKernelをつなぐ

Notebookに、この授業で使うPythonを教えます。

> **GOAL / ゴール：** Notebookが`Programming/.venv`のPythonで動く。

## まず三つの言葉

| 名前 | 意味 |
| --- | --- |
| Python | codeを動かすエンジン |
| `.venv` | この授業専用のPython環境 |
| Kernel | Notebookが今使っているPython |

> **AHA!：** `.venv`は「授業専用の道具箱」、Kernelは「今どの道具箱を使うか」の選択。

## 1. `.venv`を作る

1. VS Codeで`Programming`folderを開く。
2. Command Paletteを開く。
3. **Python: Create Environment → Venv**を選ぶ。
4. Tutorial 01で入れたPython 3を選ぶ。

| OS | Command Palette |
| --- | --- |
| Windows | `Ctrl + Shift + P` |
| macOS | `Command + Shift + P` |

Explorerに`.venv`が現れます。中身は編集せず、課題にも提出しません。

## 2. Kernelを選ぶ

1. Week 01の`.ipynb`を開く。
2. 右上の**Select Kernel**を押す。
3. **Python Environments**から`Programming/.venv`を含むPythonを選ぶ。

Code cellで確認します。

```python
import sys
print(sys.executable)
```

表示された場所に`.venv`が含まれていれば接続できています。

| 困ったとき | まず試すこと |
| --- | --- |
| `.venv`が候補にない | VS Codeを再起動し、**Python: Select Interpreter**で`.venv`を選ぶ。 |
| Jupyterのinstallを求められる | `.venv`を選んだ状態でinstallする。 |
| Cellが終わらない | Stopを押し、**Restart Kernel**を選ぶ。 |

> **CHECK / 確認：** `sys.executable`のOutputに`.venv`が含まれる。
