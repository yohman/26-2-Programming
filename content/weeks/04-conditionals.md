---
week: 4
publish_at: 2026-10-22T12:00:00+09:00
preview: true
lecture_deck_only: true
phase: WRITE
practice_mix: Human 85% · AI 15%
practice_mix_ja: 人 85% · AI 15%
title: Give your program a choice.
title_ja: 条件で変わる、プログラムの返事。
course_date: 2026-10-22
homework_due: 2026-10-28T23:59:00+09:00
homework_starter_optional: true
course_time: 13:10–14:50
overview: Practice if/else and elif, trace a rock-paper-scissors game, and start your own rule-based chatbot.
overview_ja: Notebookでif・else・elifを試す。じゃんけんの仕組みを読み解き、自分のチャットボットをつくり始める。
---
## In-Class Part 1
EN: **13:10–13:35 · Two possible replies.** Slides for 10 minutes, then practice for 15. Notebook 3.1–3.3 and exercises 1–3: comparisons, if/else, and indentation.
JP: **13:10–13:35 · 返事を二つに分ける。** 講義10分＋実習15分。Notebookの3.1〜3.3、例題1〜3。比較・if/else・インデントを試す。

## In-Class Part 2
EN: **13:35–14:05 · Several conditions.** Slides for 10 minutes, then practice for 20. Continue the same notebook: in, and/or/not, elif, and exercises 4–6. Test values on both sides of a boundary.
JP: **13:35–14:05 · 条件を組み合わせる。** 講義10分＋実習20分。同じNotebookの続き：in・and/or/not・elif、例題4〜6。境界の前後で結果を確かめる。

## In-Class Part 3
EN: **14:05–14:20 · Inside rock-paper-scissors.** Play the slide demo, then trace how Python chooses a result. The notebook’s game example is extra practice.
JP: **14:05〜14:20 · じゃんけんの裏側。** スライドのゲームを試し、Pythonのどの条件が勝敗を決めるか読む。Notebook末尾のゲーム例は、余裕があれば。

## In-Class Challenge
EN: **14:20–14:50 · Start your chatbot.** Choose its purpose and create responses, including a fallback for unexpected input. Use the optional starter or your own notebook. Spend the final 5 minutes testing with a partner. Continue this project for homework.
JP: **14:20〜14:50 · チャットボットをつくり始める。** 誰のためのBotか決め、入力に応じた返事と、想定外の入力への返事をつくる。任意のスターターでも、自作NotebookでもOK。最後の5分は隣の人に試してもらう。この続きを宿題にする。

## Take-Home Assignment
EN: **A chatbot with your own personality.**

Put **your project title and name in the first Markdown cell**.

- Choose a purpose: a campus guide, study companion, game character, or your own idea.
- Make a working conversation with **three or more distinct response paths**, a fallback for unknown input, and a way to end the conversation.
- Use `if / elif / else`. A rule-based notebook bot is enough. No AI API, website, or extra package is required.
- Show **three test conversations**, including unexpected input. Write a few sentences about one design choice and one limitation. If AI helped, note what you checked yourself.

Run all cells and save the outputs and your observations. Submit the **`.ipynb` plus required files to UNIPA by October 28 (Wed), 23:59 JST**. The starter is optional. Make the purpose, wording, and responses your own.

JP: **自分らしい、ちゃんと動くチャットボット。**

**一番上のMarkdown Cellに、作品タイトルと氏名を書いてください。**

- 大学案内、勉強の相棒、ゲームのキャラクターなど、誰のために何をするBotか決める。
- **三つ以上の返答パターン**、想定外の入力への返事、会話を終える方法を用意する。
- `if / elif / else`を使う。Notebookで動くルール型BotでOK。AIのAPI・Webサイト・追加パッケージは不要。
- **会話のテストを三つ**残す（想定外の入力を含む）。工夫と、まだできないことを数行書く。AIを使った場合は、自分で何を確認したかも一言。

全Cellを実行し、出力・観察メモを保存。**10月28日(水) 23:59までに、`.ipynb`と必要なファイルをUNIPAへ提出。** スターターは任意。テーマや言葉づかい、返事に自分らしさを出そう。

## Aha!
EN: An if/elif/else chain stops at the first match. A later, more specific rule may never be reached.
JP: if/elif/elseは、最初に当てはまった所で決まる。条件の順番だけで、同じ入力への返事も変わる。

## Takeaway
EN: A useful program handles both expected and unexpected input.
JP: 期待した入力だけでなく、想定外の入力にも返せると、使えるプログラムになる。

## Resources
- [Week 04 Lecture — Conditions, Janken & Chatbots](weeks/week-04/lecture.html) {lecture}
- [Week 04 In-Class — 条件分岐](weeks/week-04/week-04-in-class-conditionals.ipynb) {part-1}
- [同じNotebookの続き — 条件の組み合わせ](weeks/week-04/week-04-in-class-conditionals.ipynb) {part-2}
- [Chatbot starter — チャットボットをつくる（任意）](weeks/week-04/week-04-homework-chatbot.ipynb) {part-3}
- [任意のスターター / Optional starter — My Chatbot](weeks/week-04/week-04-homework-chatbot.ipynb) {homework}
