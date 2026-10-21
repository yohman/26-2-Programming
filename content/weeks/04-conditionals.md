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
EN: **Conditions: comparisons · if / elif / else · in · and / or / not**
JP: **条件分岐：比較・if / elif / else・in・and / or / not**

## In-Class Part 3
EN: **Rock-paper-scissors**
JP: **じゃんけん**

## In-Class Challenge
EN: **Chatbot**
JP: **チャットボット**

## Take-Home Assignment
EN: **A chatbot with your own personality.**

Put **your project title and name in the first Markdown cell**.

- Choose a purpose: a campus guide, study companion, game character, or your own idea.
- Make a working conversation with **three or more distinct response paths**, a fallback for unknown input, and a way to end the conversation.
- Use `if / elif / else`. A rule-based notebook bot is enough. No AI API, website, or extra package is required.
- The starter chooses a mood (normal, happy, or tired), then uses `random.choice()` to select from that mood’s reply list. Make the replies and conditions your own. No custom functions; animation is an optional beyond-class challenge.
- Briefly describe **the original features you added** and **what you would like to add or improve next**.

Run all cells and save the conversation outputs and your two short statements. Submit the **`.ipynb` plus required files to UNIPA by October 28 (Wed), 23:59 JST**. The starter is optional. Make the purpose, wording, and responses your own.

JP: **自分らしい、ちゃんと動くチャットボット。**

**一番上のMarkdown Cellに、作品タイトルと氏名を書いてください。**

- 大学案内、勉強の相棒、ゲームのキャラクターなど、誰のために何をするBotか決める。
- **三つ以上の返答パターン**、想定外の入力への返事、会話を終える方法を用意する。
- `if / elif / else`を使う。Notebookで動くルール型BotでOK。AIのAPI・Webサイト・追加パッケージは不要。
- スターターは三つの気分（ふつう・元気・おつかれ）を条件で選び、そのリストから`random.choice()`で返します。返事と条件を自分らしく変えよう。関数の定義は不要。アニメーションは授業の範囲外・任意のChallengeです。
- **自分で追加したオリジナルの機能・特徴**と、**これから加えたい機能・改善したいこと**を短く書く。

全Cellを実行し、会話の出力と上の二つの記述を保存。**10月28日(水) 23:59までに、`.ipynb`と必要なファイルをUNIPAへ提出。** スターターは任意。テーマや言葉づかい、返事に自分らしさを出そう。

## Aha!
EN: An if/elif/else chain stops at the first match. A later, more specific rule may never be reached.
JP: if/elif/elseは、最初に当てはまった所で決まる。条件の順番だけで、同じ入力への返事も変わる。

## Takeaway
EN: A useful program handles both expected and unexpected input.
JP: 期待した入力だけでなく、想定外の入力にも返せると、使えるプログラムになる。

## Resources
- [Week 04 Lecture — Conditions, Janken & Chatbots](weeks/week-04/lecture.html) {lecture}
- [Week 04 In-Class — 条件分岐](weeks/week-04/week-04-in-class-conditionals.ipynb) {part-1}
- [Chatbot starter — チャットボットをつくる（任意）](weeks/week-04/week-04-homework-chatbot.ipynb) {part-3}
- [任意のスターター / Optional starter — My Chatbot](weeks/week-04/week-04-homework-chatbot.ipynb) {homework}
