---
week: 2
publish_at: 2026-10-06T09:00:00+09:00
preview: true
phase: WRITE
practice_mix: Human 90% · AI 10%
practice_mix_ja: 人 90% · AI 10%
title: Python basics, then a live earthquake map.
title_ja: Pythonの基本から、いま起きている地震の地図へ。
course_date: 2026-10-08
homework_due: 2026-10-14T23:59:00+09:00
course_time: 13:10–14:50
overview: First get every notebook running. Then revisit your message from the future, predict what an earthquake-mapping program will do, and start your own map.
overview_ja: まず全員がNotebookを動かせるようにする。先週の「未来からのメッセージ」を完成・共有し、地震地図のコードを予想してから自分の地図をつくり始める。
---
## Lecture Flow
EN: | Time | In class |
| --- | --- |
| 13:10–13:40 | **Get Python running · 30 min** VS Code → kernel → Markdown and Code cells. |
| 13:40–14:00 | **Python basics · 20 min** Predict what a few lines of code will print. |
| 14:00–14:20 | **In-class activity · 20 min** Finish and share your message from the future. |
| 14:20–14:50 | **Earthquake challenge · 30 min** Predict, run, and change a live map. |
JP: | 時間 | 授業で行うこと |
| --- | --- |
| 13:10–13:40 | **Pythonを動かす · 30分** VS Code → Kernel → MarkdownとCodeのCell。 |
| 13:40–14:00 | **Pythonの基本 · 20分** 短いコードの出力を予想する。 |
| 14:00–14:20 | **授業内アクティビティ · 20分** 「未来からのメッセージ」を完成させて共有する。 |
| 14:20–14:50 | **地震地図チャレンジ · 30分** 予想し、動かし、自分で変える。 |

## Setup Check
EN: **Goal: everyone leaves with a working notebook.**

1. Open the `Programming` folder in VS Code. Create the `week02` folder and `week02/hello.ipynb`.
2. At the top right, choose **Select Kernel → Python Environments → `.venv`**.
3. Run `print("Hello, Week 02!")` in a Code cell. Add a Markdown cell saying what appeared.
4. Save, close, reopen, and run it again.

If stuck: no notebook controls → check the **Jupyter** extension; no `.venv` → **Python: Create Environment → Venv**; cell keeps running → **Restart Kernel**. Show the screen to Yoh or a classmate rather than waiting. [Kernel tutorial](viewer.html?file=weeks%2Fweek-01%2Ftutorials%2F04-environment-and-kernel.md) · [Notebook tutorial](viewer.html?file=weeks%2Fweek-01%2Ftutorials%2F05-jupyter-notebook.md)
JP: **今日の最優先：全員がNotebookを動かせること。**

1. VS Codeで`Programming`フォルダを開く。`week02`フォルダと`week02/hello.ipynb`を作る。
2. 右上の**Select Kernel → Python Environments → `.venv`**を選ぶ。
3. Code Cellで`print("Hello, Week 02!")`を実行。Markdown Cellに結果を一文書く。
4. 保存し、閉じて再び開き、もう一度実行する。

止まったら：Notebookの操作が出ない → **Jupyter**拡張機能を確認。`.venv`がない → **Python: Create Environment → Venv**。Cellが終わらない → **Restart Kernel**。待たずに画面を見せて相談する。[Kernelの手順](viewer.html?file=weeks%2Fweek-01%2Ftutorials%2F04-environment-and-kernel.md) · [Notebookの手順](viewer.html?file=weeks%2Fweek-01%2Ftutorials%2F05-jupyter-notebook.md)

## In-Class Notebook
EN: **Bring back your Week 01 homework.** Open your own “Message from the Future” notebook. If you did not finish it, use the same template and complete it now. Check that `input()` returns text, convert the number of years with `int()`, and display the calculated year in an f-string. Run it with two different inputs; add one Markdown sentence about what changed. Then show the result to a partner. Your idea and wording should remain your own.
JP: **先週の宿題を授業で使う。** 自分の「未来からのメッセージ」Notebookを開く。未完成なら同じテンプレートから今ここで完成させる。`input()`は文字を返すことを確認し、年数を`int()`で数に変え、計算した年をf文字列で表示する。異なる入力で二回実行し、変わった点をMarkdown Cellに一文書く。最後に隣の人へ見せる。内容と言葉は自分のものにする。

## In-Class Challenge
EN: **Last 30 minutes: live earthquake map.** Before Yoh runs the code, predict what the `latitude`, `longitude`, `mag`, and `place` columns will become on a map. Open the template, run it once using the USGS feed, then change at least one visible choice such as the minimum magnitude, marker color, or map center. The supplied 2024 CSV is an offline fallback. Loops and libraries in the template are provided; today your job is to understand the inputs, output, and the lines you change.
JP: **最後の30分：ライブ地震地図。** Yohがコードを実行する前に、`latitude`、`longitude`、`mag`、`place`が地図上で何になるか予想する。テンプレートを開き、USGSのデータで一度実行する。その後、表示する最小マグニチュード、点の色、地図の中心などを一つ以上変える。付属の2024年CSVはネット接続できないときの予備データ。ループやライブラリの部分は用意してある。今日は入力・出力・自分が変えた行を理解する。

## Take-Home Assignment
EN: Make the earthquake-map template useful for **an audience you choose**.

1. Give your map a clear title and change **at least two visible settings**. Explain why.
2. Run the notebook from top to bottom. In Markdown, note your prediction, one thing you noticed on the map, and whether you used live or fallback data.
3. Submit the working `.ipynb` to **UNIPA**. Include the CSV only if your notebook needs that local file. AI can help explain an error; verify the final map yourself.
JP: 地震地図のテンプレートを、**自分で決めた相手**のための地図にする。

1. 分かりやすいタイトルを付け、**見た目に現れる設定を二つ以上**変える。変えた理由も書く。
2. Notebookを上から最後まで実行する。Markdownに事前の予想、地図から気づいたこと、ライブデータと予備データのどちらを使ったかを書く。
3. 動く`.ipynb`を**UNIPA**へ提出。ローカルCSVが必要な場合だけ一緒に提出する。AIにエラーの意味を聞いてもよいが、最後の地図は自分で確かめる。

## Aha!
EN: `input()` looks like a number when you type `5`, but Python receives the text `"5"`. One conversion changes what the program can calculate.
JP: `input()`に`5`と入力しても、Pythonが受け取るのは文字の`"5"`。一度変換すると計算できる。

## Takeaway
EN: A program becomes useful when you can identify its input, change a value, and explain the output.
JP: 入力を見つけ、値を変え、出力を説明できると、コードは自分の道具になる。

## Resources
- [Week 02 Lecture — Python Basics & Earthquake Map](weeks/week-02/lecture.html) {lecture}
- [Week 01 Homework — Message from the Future](weeks/week-01/week-01-homework-message-from-the-future.ipynb) {notebook}
- [Week 02 Challenge — Live Earthquake Map Template](weeks/week-02/week-02-challenge-live-earthquake-map.ipynb) {challenge}
- [Earthquake data — 2024 offline fallback](weeks/week-02/all-month-earthquakes.csv) {data}
- [Week 02 Homework — Continue the Earthquake Map Template](weeks/week-02/week-02-challenge-live-earthquake-map.ipynb) {homework}
