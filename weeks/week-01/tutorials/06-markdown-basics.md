# Tutorial 06 — Markdownで説明を書く

MarkdownはNotebookのText cellで使う、簡単な書式です。課題ではcodeだけでなく、**考えたことと分かったこと**も残します。

> **GOAL / ゴール：** 見出し、強調、listを使って読みやすい説明を書く。

## CodeとMarkdown

| Cell | 誰に向けるか | 例 |
| --- | --- | --- |
| Code | Python | `print("Hello")` |
| Markdown | 読む人 | 「名前を表示します」 |

## これだけ覚える

| 書き方 | 結果 |
| --- | --- |
| `# Title` | 大きな見出し |
| `## Section` | 小さな見出し |
| `**important**` | **強調** |
| `- item` | bullet list |
| `1. step` | numbered list |
| `` `print()` `` | inline code |
| `[Python](https://python.org)` | link |

> **TIP / ヒント：** `#`、`-`、`1.`のあとにはspaceを一つ入れる。

## 一つの例

Markdown cellへ貼り、自分の内容に変えます。

```markdown
# Aki's first Notebook

今日は **Pythonを動かす** ところまで進みました。

試したこと：
- messageを変えた
- Errorを一つ読んだ
- もう一度Run Allした
```

`Shift + Enter`で、書式が整った表示へ変わります。

## Mini exercise

自分のMarkdown cellに次の三つを入れてください。

1. 自分の名前を含む見出し
2. 今日分かったことを一文
3. 次にPythonで作りたいものを三つのbullet list

> **AHA!：** 良いNotebookは「動くcode」だけでなく、「なぜそうしたか」も読める。

> **CHECK / 確認：** 見出し、強調、listを使った自分のMarkdown cellが一つある。
