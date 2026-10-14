---
week: 3
publication_hold: true
publish_at: 2026-10-13T09:00:00+09:00
preview: true
phase: WRITE
practice_mix: Human 80% · AI 20%
practice_mix_ja: 人 80% · AI 20%
title: Collections: a playlist, a record, your own guide.
title_ja: リストと辞書で、私のガイドをつくる。
course_date: 2026-10-15
homework_due: 2026-10-21T23:59:00+09:00
homework_starter_optional: true
course_time: 13:10–14:50
overview: Explore real data, then practice lists, dictionaries, and combining them. Build a personal guide in class; investigate API data for homework.
overview_ja: 実データをのぞいてから、リスト・辞書・組み合わせを実習。授業では「私の〇〇ガイド」、宿題ではAPIデータで小さな発見を。
---
## Lecture Flow
EN: | Time | Explain, then do |
| --- | --- |
| 13:10–13:25 | **Opening + Part 1** Explore real web data; recognize lists. |
| 13:25–13:45 | **Part 1 notebook** Indexing, totals, edits, and slicing. |
| 13:45–13:55 | **Part 2 lecture** Names and values: dictionaries. |
| 13:55–14:15 | **Part 2 notebook** Retrieve, add, change, and combine values. |
| 14:15–14:20 | **Part 3 lecture** Earthquake records and your own collection. |
| 14:20–14:50 | **Part 3 challenge** Build a personal recommendation guide. |
JP: | 時間 | 説明の後に、自分で試す |
| --- | --- |
| 13:10–13:25 | **導入＋Part 1 講義** Webの実データを探索し、リストを見つける。 |
| 13:25–13:45 | **Part 1 実習** 添字・合計・編集・スライス。 |
| 13:45–13:55 | **Part 2 講義** 名前と値を組にする辞書。 |
| 13:55–14:15 | **Part 2 実習** 値を取り出し、追加・変更する。 |
| 14:15–14:20 | **Part 3 講義** 地震のデータから、自分のコレクションへ。 |
| 14:20–14:50 | **Part 3 チャレンジ** 「私の〇〇ガイド」をつくる。 |

## Exploration
EN: **Start with Toei’s live bus map.** Fetch reported latitude/longitude without an account or key. Switch from Map to Pretty to reveal the decoded records, then compare trains, which report station IDs instead. Explore weather, earthquakes, Pokémon, and LA crime records too. Saved examples are clearly labelled.
JP: **まず、都営バスのライブ地図から。** 登録・APIキーなしで、報告された緯度・経度を取得。MapからPrettyへ切り替えてデコードされたデータを見て、駅IDで位置を表す電車とも比べる。天気・地震・ポケモン・LAの犯罪記録も探索。保存例はライブと区別して表示。

## In-Class Part 1
EN: **Part 1 — Lists · 20 min.** Work through scores, indexing, list edits, and slicing. Complete four short exercises. Download the notebook, select your kernel, and run from the top.
JP: **Part 1 — リスト · 20分。** 点数の合計から、添字・要素の編集・スライスへ。四つの練習に取り組む。Notebookをダウンロードし、Kernelを選んで上から実行する。

## In-Class Part 2
EN: **Part 2 — Dictionaries · 20 min.** Retrieve scores by subject, update the original height example, and build a profile with a list inside it. Tuples are optional.
JP: **Part 2 — 辞書 · 20分。** 科目名で点数を取り出し、元教材の身長データを修正。リストを含む自己紹介もつくる。タプルはOptional。

## In-Class Part 3
EN: **Part 3 — My guide · last 30 min.** Read a list of earthquake dictionaries, then use the same structure for a collection of your own. Homework is a separate real-data investigation.
JP: **Part 3 — 私のガイド · 最後の30分。** 地震の「辞書のリスト」を読み、同じ構造で自分のコレクションをつくる。宿題は別の実データ探索。

## In-Class Challenge
EN: Choose a theme and audience: cafés, games, music, study spots, or an imagined world. Create **three records** in a list of dictionaries. Use the supplied display loop, try one update/addition, and show a partner. No GitHub setup, CSV, or new packages required.
JP: カフェ、ゲーム、音楽、勉強場所、架空の世界など、テーマと見せたい相手を決める。「辞書のリスト」で**三件**つくる。用意した表示用のループを使い、一つ更新・追加して隣の人に見せる。GitHubの設定、CSV、追加パッケージは不要。

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
- [Week 03 Lecture — Lists, Dictionaries & My Guide](weeks/week-03/lecture.html) {lecture}
- [Part 1 — リスト / Lists](weeks/week-03/week-03-in-class-part-01-lists.ipynb) {part-1}
- [Part 2 — 辞書 / Dictionaries](weeks/week-03/week-03-in-class-part-02-dictionaries.ipynb) {part-2}
- [Part 3 — 私のガイド / My Guide](weeks/week-03/week-03-in-class-part-03-my-guide.ipynb) {part-3}
- [任意のスターター / Optional starter — データで見つけた、小さな発見](weeks/week-03/week-03-homework-data-discovery.ipynb) {homework}
