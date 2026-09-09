# Week 01 — Python を「自分のコンピュータで動かす」ための道順

> **今日のゴール：緑のチェックが四つそろうこと。** 速さではなく、一つずつ確認します。途中で止まることは普通です。止まった場所を見せれば、次の一手を一緒に見つけられます。

## まず知っておく三つの役割

| 名前 | たとえ | 今日すること |
|---|---|---|
| **Python** | 命令を実際に実行するエンジン | コンピュータに入れる |
| **VS Code** | コードを書く机 | インストールして開く |
| **`.venv`** | この授業・このフォルダ専用の小さな道具箱 | VS Codeに作ってもらう |

`.venv` は難しい設定ではありません。別の授業や将来のプロジェクトの道具と混ざらないようにする、フォルダごとの安全な箱です。

## Checkpoint 0 — フォルダを作る

1. 分かりやすい場所に `programming-2026` フォルダを作る。
2. VS Codeを開く。
3. **File → Open Folder…** で `programming-2026` を開く。
4. 「このフォルダを信頼しますか」と聞かれたら、自分で作った授業用フォルダであることを確認してから信頼する。

**✅ 画面左に `programming-2026` が見えたら、Checkpoint 0 は完了。**

## Checkpoint 1 — Python と VS Code を用意する

まだ入っていない人だけ、次をインストールします。

- [Python 3](https://www.python.org/downloads/) — Python 3 の最新版を選ぶ
- [Visual Studio Code](https://code.visualstudio.com/) — 自分のOS用を選ぶ

インストール後は VS Code を一度終了して開き直します。`python` という古いOS標準の表示が見えても慌てなくて大丈夫です。今日使うものは、次の手順で自分で選ぶ Python 3 です。

**✅ VS Code が起動できたら、Checkpoint 1 は完了。**

## Checkpoint 2 — Python と Jupyter を VS Code に追加する

1. 左側の **Extensions** を開く。
2. `Python` を検索し、発行元が **Microsoft** の拡張機能をインストールする。
3. `Jupyter` を検索し、発行元が **Microsoft** の拡張機能をインストールする。
4. 必要なら VS Code を再読み込みする。

**✅ 左下または Python の表示に、利用できる Python 3 が見えたら、Checkpoint 2 は完了。**

## Checkpoint 3 — この授業用の `.venv` を作る

1. `Cmd + Shift + P`（Windows は `Ctrl + Shift + P`）を押す。
2. **Python: Create Environment** を選ぶ。
3. **Venv** を選ぶ。
4. 表示された Python 3 を選ぶ。
5. 完了を待つ。フォルダの中に `.venv` が現れます。これは提出物ではありません。

うまく選ばれないときは、VS Code 右下の Python 表示を押すか、コマンドパレットで **Python: Select Interpreter** を実行して、`programming-2026/.venv` を選びます。

**✅ VS Code が `.venv` の Python を選んでいれば、Checkpoint 3 は完了。**

## Checkpoint 4 — ノートブックを動かす

1. Week 01 の `.ipynb` ファイルを開く。
2. 右上の **Select Kernel** を押す。
3. `programming-2026/.venv` の Python を選ぶ。
4. `print("Hello, world!")` のセルを実行する。
5. もし「Jupyter / ipykernel をインストールしますか」と聞かれたら、**この `.venv` にインストール**を選ぶ。

**✅ セルの下に `Hello, world!` が出たら、今日の技術セットアップは成功です。**

## 困ったときのカード

| 見えていること | まずすること |
|---|---|
| Python が一覧にない | VS Code を再起動 → **Python: Select Interpreter** → それでもなければ Python 3 のインストールを確認 |
| セルが実行できない | 右上の **Select Kernel** で `.venv` を選ぶ |
| `ModuleNotFoundError` | そのノートブックが別の Python を使っている合図。Kernel を `.venv` に戻す |
| どこで止まったか分からない | 画面をそのまま見せる。エラーメッセージ、左下のPython名、右上のKernel名が手がかり |

## 最後の一言

「Pythonを入れた」だけでは、まだプログラムは動きません。**フォルダ、Python、`.venv`、Kernel がつながった**ときに、初めてこのコンピュータは自分のコードを実行できる状態になります。
