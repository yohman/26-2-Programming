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

## Tutorials
- [Pythonをインストールする / Install Python](weeks/week-01/tutorials/01-install-python.md) {tutorial}
- [VS Codeを準備する / Set up VS Code](weeks/week-01/tutorials/02-install-vscode.md) {tutorial}
- [授業フォルダをつくる / Create the course workspace](weeks/week-01/tutorials/03-course-workspace.md) {tutorial}
- [`.venv`とKernelをつなぐ / Environment and kernel](weeks/week-01/tutorials/04-environment-and-kernel.md) {tutorial}
- [Jupyter Notebookの使い方 / Use a notebook](weeks/week-01/tutorials/05-jupyter-notebook.md) {tutorial}
- [Markdownで説明を書く / Markdown basics](weeks/week-01/tutorials/06-markdown-basics.md) {tutorial}
- [Python BasicsとローカルChallenge / Python basics](weeks/week-01/tutorials/07-python-basics-and-challenges.md) {tutorial}

## In-Class Notebook
EN: **Bring back your Week 01 homework.** Open your own “Message from the Future” notebook. If you did not finish it, use the same template and complete it now. Check that `input()` returns text, convert the number of years with `int()`, and display the calculated year in an f-string. Run it with two different inputs; add one Markdown sentence about what changed. Then show the result to a partner. Your idea and wording should remain your own.
JP: **先週の宿題を授業で使う。** 自分の「未来からのメッセージ」Notebookを開く。未完成なら同じテンプレートから今ここで完成させる。`input()`は文字を返すことを確認し、年数を`int()`で数に変え、計算した年をf文字列で表示する。異なる入力で二回実行し、変わった点をMarkdown Cellに一文書く。最後に隣の人へ見せる。内容と言葉は自分のものにする。

## In-Class Challenge
EN: **Last 30 minutes: start your homework map.** Download a CSV from the [USGS CSV download page](https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php) (**Past Day → All Earthquakes**) and put it beside the notebook. Run the starter: read the CSV, loop through its rows, and place one Folium marker at each latitude/longitude. Then choose an improvement:

- Change the base map.
- Replace pins with circles.
- Color markers by magnitude.
- Filter earthquakes by magnitude or location.

Start one change in class; finish the same notebook as homework. The supplied 2024 CSV is a backup dataset, not current earthquakes.
JP: **最後の30分：宿題の地図づくりを始める。** [USGSのCSVダウンロードページ](https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php)の**Past Day → All Earthquakes**からCSVを保存し、Notebookと同じフォルダに置く。まずテンプレートを実行：CSVを読み、各行をループして、緯度・経度にFoliumのマーカーを一つずつ置く。その地図を自分で改良しよう。

- ベースマップを変える。
- ピンを円に変える。
- マグニチュードによって色を変える。
- マグニチュードや場所で絞り込む。

授業で一つ改良を始め、**同じNotebookを宿題として仕上げる**。付属の2024年CSVは予備データで、現在の地震ではありません。

## Take-Home Assignment
EN: **Continue the map you started in class—this is the same assignment.** Make it useful for an audience you choose. [USGS CSV download page](https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php)

1. Give your map a title and make **at least two improvements**: a different base map, circles, magnitude colors, or a filter. Your own idea is welcome.
2. In Markdown, explain who the map is for, why you made those changes, and one observation. Record the CSV source and download date (or identify the 2024 backup).
3. Run every cell, save the outputs, and submit the completed `.ipynb` **and the CSV it reads** to **UNIPA**. AI may explain an error; check the resulting map yourself.
JP: **授業で始めた地図を、そのまま宿題として完成させる。別の課題ではありません。** 自分で決めた相手に伝わる地図にしよう。[USGSのCSVダウンロードページ](https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php)

1. タイトルを付け、**二つ以上改良する**。ベースマップ、円、色分け、フィルターなどから選ぶ。自分のアイデアでもOK。
2. Markdownに「誰に見せる地図か」「なぜその改良をしたか」「地図から気づいたこと」を書く。CSVの出典とダウンロード日も記録する（予備データなら2024年のデータと明記）。
3. 全Cellを実行して出力を保存し、完成した`.ipynb`と**読み込んだCSV**を**UNIPA**へ提出する。AIにエラーの意味を聞いてもよいが、地図は自分で確かめる。

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
