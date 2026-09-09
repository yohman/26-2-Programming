---
week: 1
publish_at: 2026-09-29T09:00:00+09:00
preview: true
phase: WRITE
practice_mix: Human 85% · AI 10% · Agent 5%
practice_mix_ja: 人 85% · AI 10% · エージェント 5%
title: Make the computer say something.
title_ja: コンピュータに「してほしいこと」を伝える。
course_date: 2026-10-01
course_time: 13:10–14:50
overview: Build your personal Python workspace, run your first notebook, and make a small calculator that someone else can use.
overview_ja: 自分のPython作業環境をつくり、最初のノートブックを実行し、誰かが使える小さな計算機をつくる。
---
## Lecture Flow
EN:
| Time | Make this happen |
| --- | --- |
| 0–10 | Short lecture: one instruction → execution → output. See the destination: four green checks. |
| 10–40 | Set up calmly: course folder → Python → VS Code → Python/Jupyter extensions. |
| 40–50 | Create `.venv`; select its interpreter and notebook kernel; run `Hello, world!`. |
| 50–70 | First Python notebook: write and predict `print()`, strings, numbers, variables, and arithmetic. |
| 70–100 | Make and partner-run a Mini Personal Calculator; share, complete the setup receipt, and write an exit note. |

Students who finish early become **check partners**, not substitute technicians.
JP:
| 時間 | すること |
| --- | --- |
| 0〜10分 | Short lecture：一つの命令 → 実行 → 出力。「緑のチェック四つ」という到達点を見る。 |
| 10〜40分 | 落ち着いて準備する：授業フォルダ → Python → VS Code → Python/Jupyter拡張機能。 |
| 40〜50分 | `.venv`を作り、インタープリタとNotebook Kernelに選び、`Hello, world!`を実行する。 |
| 50〜70分 | 最初のPythonノートブック：`print()`、文字列、数値、変数、計算を予想して書く。 |
| 70〜100分 | ミニ生活計算機を作り、ペアで実行確認、共有、セットアップ完了票、退出メモ。 |

早く終わった学生は、代わりに設定する人ではなく**確認パートナー**になる。
## In-Class Notebook
EN: Set up your own Python notebook, then write and run your first small programs. You will work with output, values, variables, and input.
JP: 自分のPythonノートブックを準備し、最初の小さなプログラムを書いて実行する。出力、値、変数、入力を扱う。
## In-Class Challenge
EN: Make a Mini Personal Calculator: two inputs, one useful calculation, and one clear result. A partner should be able to run it.
JP: 二つの入力、一つの役に立つ計算、読みやすい結果を持つミニ生活計算機を作る。ペアが実行できる状態にする。
## Take-Home Assignment
EN: Make a first tiny tool that is *not* the class calculator: a personal card, mini story, game-start screen, plan, or other one-screen experience. It should use your own words and inputs, then create one clear output someone will want to see. Submit the notebook and one screenshot. Be ready to show it in Week 02.
JP: 授業内の計算機とは別に、はじめてのミニツールをつくる。プロフィールカード、ミニストーリー、ゲーム開始画面、予定カードなど、1画面で見せられる自分らしい作品にする。自分の言葉と入力を使い、見せたくなる一つの出力をつくろう。ノートブックとスクリーンショットを提出し、Week 02で紹介できるようにする。
## Aha!
EN:
```python
score = score + 5
```

This is not a mathematical claim. It replaces the value currently remembered under `score`.
JP:
```python
score = score + 5
```

これは数式の主張ではない。`score`という名前で今覚えている値を、新しい値に置き換える命令である。
## Takeaway
EN: A program is a sequence of small instructions whose values change in a traceable way.
JP: プログラムは、追跡できる形で値を変えていく小さな命令の連なりである。
## Resources
- [Week 01 In-Class — First Python](weeks/week-01/week-01-in-class-first-python.ipynb) {notebook}
- [Week 01 Challenge — Mini Personal Calculator](weeks/week-01/week-01-challenge-mini-personal-calculator.ipynb) {challenge}
- [Week 01 Take-Home — My First Tiny Tool](weeks/week-01/week-01-take-home-my-first-tiny-tool.ipynb) {homework}
- [Week 01 Setup — Python, VS Code, and Jupyter](weeks/week-01/week-01-setup-python-vscode-jupyter.md) {support}
- [Week 01 Lecture — First Python](weeks/week-01/week-01-lecture-first-python.pdf) {lecture}
