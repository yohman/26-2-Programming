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
| 13:10–13:40 · 30 min | **Everyone gets running.** Open VS Code, select a kernel, create a new `.ipynb`, and run two cells. Ask for help as soon as one step fails. |
| 13:40–14:00 · 20 min | **Python basics.** `print()`, `input()`, arithmetic, variables, f-strings, text and numbers, lists, and dictionaries. Use the Playground to predict outputs. |
| 14:00–14:20 · 20 min | **Message from the future.** Open last week's homework, finish or improve it, test two inputs, and show a partner. |
| 14:20–14:50 · 30 min | **Earthquake challenge.** Predict the map code, watch the live demonstration, then run and change your own template. |
JP: | 時間 | 授業で行うこと |
| --- | --- |
| 13:10–13:40 · 30分 | **全員で環境を整える。** VS Codeを開き、Kernelを選び、新しい`.ipynb`を作って二つのCellを動かす。止まったらすぐに声をかける。 |
| 13:40–14:00 · 20分 | **Pythonの基本。** `print()`、`input()`、計算、変数、f文字列、文字と数、リスト、辞書。Playgroundで出力を予想する。 |
| 14:00–14:20 · 20分 | **未来からのメッセージ。** 先週の宿題を開いて完成・改善し、二通りで試して隣の人に見せる。 |
| 14:20–14:50 · 30分 | **地震地図チャレンジ。** コードの結果を予想し、ライブデモを見て、テンプレートを自分で動かし変更する。 |

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
EN: **Your earthquake map.** Continue the in-class template at home. Choose a purpose or audience for your map, change at least two visible settings, and give it a clear title. Run the notebook from top to bottom. In Markdown, record (1) your prediction, (2) two changes and why you made them, (3) one observation from the map, and (4) whether you used live or fallback data. Submit the working `.ipynb` to UNIPA by Wednesday, October 14 at 23:59 JST. Include the CSV only if your notebook depends on that local file. AI may help explain an error, but check the final output yourself.
JP: **自分の地震地図。** 授業で使ったテンプレートを家で続ける。誰に何を見せたい地図かを決め、見た目に現れる設定を二つ以上変更し、分かりやすいタイトルを付ける。Notebookを上から最後まで実行する。Markdownに①事前の予想、②変えた二つの点と理由、③地図から気づいたことを一つ、④ライブデータか予備データのどちらを使ったかを書く。**10月14日（水）23:59 JST**までに、動く`.ipynb`をUNIPAへ提出する。ローカルCSVに依存する場合だけ、そのCSVも一緒に提出する。AIにエラーの意味を聞いてもよいが、最終結果は自分で確かめる。

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
