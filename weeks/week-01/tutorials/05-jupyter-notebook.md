# Tutorial 05 — Jupyter Notebookを使う

`.ipynb`は、**説明・Python code・実行結果**を一つにまとめるNotebook fileです。

> **GOAL / ゴール：** Code cellとMarkdown cellを使い、最初のPythonを実行する。

## 二種類のCell

| Cell | 役割 |
| --- | --- |
| Code | コンピュータへの命令を書く |
| Markdown | 人が読む説明や観察を書く |

> **AHA!：** Code cellはコンピュータへ、Markdown cellは未来の自分や読む人へ書く。

## よく使う操作

| したいこと | 操作 |
| --- | --- |
| Cellを追加 | **+ Code** / **+ Markdown** |
| 一つ実行 | ▶ または`Shift + Enter` |
| 全部実行 | **Run All** |
| 最初の状態へ戻す | **Restart Kernel** |
| 保存 | `Ctrl + S` / `Command + S` |

Notebookは上から順番に実行します。

## Hello, world!

Code cellを作り、実行します。

```python
print("Hello, world!")
```

文字を自分の言葉へ変え、もう一度実行してください。

> **AHA!：** codeを一か所変えると、Outputも変わる。Programmingはこの因果関係を自分で作ること。

## 30秒Experiment

1. `print()`を二行にする。
2. 引用符を一つ消して実行する。
3. Errorを読んだら引用符を戻す。
4. Markdown cellに「何が起きたか」を一文書く。

> **CHECK / 確認：** Outputを出し、Markdownを一文書き、保存してからRun Allできる。
