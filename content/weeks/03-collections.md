---
week: 3
publication_hold: false
lecture_deck_only: true
publish_at: 2026-10-13T09:00:00+09:00
preview: true
phase: WRITE
practice_mix: Human 80% · AI 20%
practice_mix_ja: 人 80% · AI 20%
title: Reading real API data with Python.
title_ja: APIのデータを、Pythonで読む。
course_date: 2026-10-15
homework_due: 2026-10-21T23:59:00+09:00
homework_starter_optional: true
course_time: 13:10–14:50
overview: Look inside live bus and weather data. Learn how strings, numbers, lists, and dictionaries describe the world, then practice in three notebooks. Homework: a small discovery using API data.
overview_ja: 都営バスや天気の実データから、文字列・数値・リスト・辞書の役割を知る。三つのNotebookで手を動かし、宿題ではAPIデータから自分なりの発見を見せる。
---
## Exploration
EN: Fetch bus, weather, music, and other API data. Compare the JSON with maps, charts, and listening links.
JP: バス・天気・音楽などのAPIデータを取得。JSONの中身と、地図・グラフ・試聴リンクを見比べよう。

## In-Class Part 1
EN: **Part 1 — Lists · 20 min.** Select, edit, and slice items.
JP: **Part 1 — リスト · 20分。** 要素を取り出す・編集する・スライスする。

## In-Class Part 2
EN: **Part 2 — Dictionaries · 20 min.** Look up and update values by key.
JP: **Part 2 — 辞書 · 20分。** キーで値を取り出し、追加・変更する。

## In-Class Part 3
EN: **Part 3 — My guide · 30 min.** Combine lists and dictionaries to make your own guide.
JP: **Part 3 — 私のガイド · 30分。** リストと辞書を組み合わせ、自分のガイドをつくる。

## In-Class Challenge
EN: Choose a theme, create **three records**, and share with a partner.
JP: 好きなテーマで**三件**つくり、隣の人に見せよう。

## Take-Home Assignment
EN: **A small discovery with real data.**

- Choose an Explore example or another public API and a question that interests you.
- Bring the data into Python, read it using lists/dictionaries, and show something: a summary, table, chart, or map. One is enough.
- Write a few sentences about your discovery, one value you checked, and a limitation. Include the source URL.

Run all cells and save the outputs. Submit your **`.ipynb` and any required files to UNIPA by October 21, 23:59 JST**. The starter below is optional. You are encouraged to create your own `.ipynb` from scratch. A saved JSON response is fine if fetching fails; note when it was retrieved. No API key required. If you use AI, briefly note what it helped with.

JP: **データで見つけた、小さな発見。**

- Exploreの例、または別の公開APIから、気になるデータと問いを選ぶ。
- Pythonに取り込み、リスト・辞書を使って読み、何かを見せる。要約・表・グラフ・地図のどれか一つでOK。
- 発見したこと、確かめた値、データの限界を短く書く。出典URLも添える。

全Cellを実行し、出力を保存。**10月21日(水) 23:59までに、`.ipynb`と必要なファイルをUNIPAへ。** 下のスターターは任意です。**自分で新しい`.ipynb`を一から作ることも歓迎・おすすめです。** 取得できなければ保存したJSONでもOK（取得日を記載）。APIキーは不要。AIを使った場合は、何に使ったか一言添える。

## Aha!
EN: `guide[0]["name"]` makes two choices: the first record, then its name.
JP: `guide[0]["name"]`は二回選んでいる。最初の一件、その中の名前。

## Takeaway
EN: Lists organize by position; dictionaries organize by meaning. Combining them lets the same code handle many records.
JP: リストは順番、辞書は意味で取り出す。組み合わせると、同じコードで何件も扱える。

## Resources
- [Week 03 Lecture — APIs, Data Types & Collections](weeks/week-03/lecture.html) {lecture}
- [Part 1 — リスト / Lists](weeks/week-03/week-03-in-class-part-01-lists.ipynb) {part-1}
- [Part 2 — 辞書 / Dictionaries](weeks/week-03/week-03-in-class-part-02-dictionaries.ipynb) {part-2}
- [Part 3 — 私のガイド / My Guide](weeks/week-03/week-03-in-class-part-03-my-guide.ipynb) {part-3}
- [任意のスターター / Optional starter — データで見つけた、小さな発見](weeks/week-03/week-03-homework-data-discovery.ipynb) {homework}
