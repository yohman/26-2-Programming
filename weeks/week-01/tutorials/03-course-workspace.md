# Tutorial 03 — 授業フォルダをつくる

授業のNotebookとdataを、一つの場所にまとめます。

> **GOAL / ゴール：** `Programming/week01/`を作り、`Programming`全体をVS Codeで開く。

## 1. 二つのfolderを作る

Documentsの中に、次の構造を作ります。

```text
Programming/
└── week01/
```

WindowsはFile Explorer、macOSはFinderを使います。今後は同じ場所に`week02`、`week03`を追加します。

## 2. VS Codeで開く

1. VS Codeで**File → Open Folder…**を選ぶ。
2. `Programming`を選ぶ。
3. Workspace Trustが出たら、自分で作ったfolderであることを確認して信頼する。

左のExplorerに`Programming`と`week01`が見えれば成功です。

> **AHA!：** Notebook一つではなくfolder全体を開くと、VS CodeはPython環境、Notebook、CSVの関係をまとめて見つけられる。

## 3. Week 01のfileを置く

downloadしたWeek 01の`.ipynb`は`week01`へ移します。

```text
Programming/
├── .venv/          ← 次のTutorialで作る
└── week01/
    ├── week-01-in-class-first-python.ipynb
    └── week-01-challenge-mini-personal-calculator.ipynb
```

`.venv`は`week01`の中ではなく、`Programming`の直下に置きます。

> **CHECK / 確認：** VS CodeのExplorerに`Programming`、`week01`、二つのNotebookが見える。
