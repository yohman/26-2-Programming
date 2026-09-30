---
title: Course guide
title_ja: この授業について
dek: Learn to write code yourself, work thoughtfully with AI, and direct an agent without losing responsibility for the result.
dek_ja: 自分でコードを書き、AIを考えて使い、結果への責任を持ってエージェントに仕事を任せる。初めてのプログラミングを、つくる力につなげます。
---
## この授業でできるようになること / What you will learn
EN: By the end of the course, you should be able to:

- Read, trace, explain, and write small Python programs using values, collections, conditions, loops, functions, and notebooks.
- Turn a question or need into code that produces a useful, inspectable result.
- Use AI completion for a bounded task, then check its suggestions against your own reasoning and tests.
- Brief a coding agent with a goal, context, constraints, and acceptance checks; review and improve what it changes.
- Show another person how your program works, what you verified, and where its limits are.

JP: 授業が終わるころには、次のことができるようになります。

- 値、リスト、条件分岐、ループ、関数、Notebookを使った小さなPythonプログラムを、読み、追い、説明し、書く。
- 問いや必要を、確かめられる結果を出すコードに変える。
- AI補完を小さな作業に使い、提案を自分の考えとテストで判断する。
- 目標・文脈・制約・受け入れ基準を伝えてエージェントを動かし、変更を読み、改善する。
- プログラムの動き、確かめたこと、まだできないことを他の人に説明する。
## 三つのコーディング / Three ways of coding
EN: **Human coding** comes first: predict what code will do, run it, and explain the difference. **AI completion** can help you extend, debug, or improve a small part, but you decide what to keep. **Agent-based coding** means describing a bounded job and checking the agent's changes against explicit tests. The balance shifts through the semester; human understanding and verification never disappear.

Each 100-minute class moves from a short lecture into an in-class notebook and a final 30-minute challenge. The take-home task asks you to make something different with that week's ideas.

JP: **Human Coding**では、まず自分でコードを読み、動きを予想し、書いて確かめます。**AI Completion**では、小さな拡張・修正・説明をAIに手伝わせ、採用するかは自分で決めます。**Agent-Based Coding**では、範囲を決めて仕事を頼み、変更内容とテスト結果を確認します。学期後半ほどAIやエージェントを多く使いますが、人の理解と検証は最後まで必要です。

100分の授業は、短い講義、授業内Notebook、最後の30分のチャレンジで進みます。持ち帰り課題では、その週の考え方を使って授業内とは別のものをつくります。
## 毎週の課題 / Weekly assignments
EN: Weeks 01–12 each have one take-home assignment, worth **0–3 points**. There are 12 assignments, so the maximum is 36 points. Your weekly-assignment score contributes **60%** of the course grade: `points earned ÷ 36 × 60`.

Aim for a small, complete notebook rather than a large unfinished one. Each prompt says what to make and what files to submit. The deadline for that week's assignment is the one shown in UNIPA.

JP: Week 01〜12は、毎週一つの持ち帰り課題を**0〜3点**で評価します。12回で満点は36点。課題部分は成績の**60%**で、`獲得点 ÷ 36 × 60`で計算します。

大きな未完成品より、小さくても最後まで動くNotebookを目指してください。つくるものと提出ファイルは各週の課題に書いてあります。締切はUNIPAの表示を確認してください。
## 最終プロジェクト / Final project
EN: Make one small Python work of your own: a useful tool, data investigation, visualisation, or other focused idea. A clear question or user matters more than extra features. A GUI is optional.

| When | Milestone |
| --- | --- |
| Week 10 · Dec 3 | Collect one possible question or user need. |
| Week 11 · Dec 10 | Submit a one-page scope and test plan as part of the weekly assignment. |
| Week 12 · Dec 17 | Submit a working prototype and test evidence as the weekly assignment. |
| Week 13 · Jan 7 | Test with a peer, finish, and submit the project through UNIPA. |

Submit runnable files, a short README, three checks, and a brief record of what you wrote yourself, what AI suggested, and what an agent changed. See the [full project brief](viewer.html?file=content%2Ffinal-project.md&title=Final+Project&return=guide.html%23guide-final-project) for the exact deliverables. The project is worth **20%**. Week 13 has no separate 3-point homework.

JP: 自分の小さなPython作品を一つつくります。便利な道具、データの調査、可視化など、題材は選べます。機能の多さより、明確な問いや使う人が大切です。GUIは必須ではありません。

| 時期 | 進め方 |
| --- | --- |
| Week 10 · 12月3日 | 問い、または使う人の困りごとの候補を一つ見つける。 |
| Week 11 · 12月10日 | 範囲とテスト計画を1ページにまとめ、週課題として提出。 |
| Week 12 · 12月17日 | 動く試作品とテストの証拠を週課題として提出。 |
| Week 13 · 1月7日 | 仲間に試してもらい、完成版をUNIPAで提出。 |

実行できるファイル、短いREADME、三つの確認、人が書いた部分・AIの提案・エージェントの変更についての簡潔な記録を提出します。詳しくは[最終プロジェクトの要項](viewer.html?file=content%2Ffinal-project.md&title=Final+Project&return=guide.html%23guide-final-project)を見てください。プロジェクトは**20%**。Week 13に別の3点課題はありません。
## 授業内の最終チャレンジ / Final in-class challenge
EN: In Week 14 (Jan 14), you will complete an individual, practical Python challenge during the 100-minute class. You will predict or explain code, repair and extend a supplied notebook, test your result, and explain a decision. The challenge is **20%** of the course grade. It is separate from the project; you do not have to build another project in the exam.

Normal editor completion is part of today's coding environment. The assessment is of your understanding, changes, checks, and explanation—not just a finished output. Any additional rules about AI chat or agents will be stated with the challenge in class.

The 20 points are divided equally: code reading and prediction (5), repair or extension (5), verification (5), and your explanation of the result and tool use (5).

JP: Week 14（1月14日）の100分間に、**個人で行うPythonの実践チャレンジ**を実施します。コードの動きを予想・説明し、配布されるNotebookを修正・拡張し、結果をテストして判断を説明します。成績の**20%**です。プロジェクトとは別で、試験中にもう一つのプロジェクトをつくる必要はありません。

通常のエディタ補完を止める必要はありません。完成した出力だけでなく、理解、変更、確認、説明を評価します。AIチャットやエージェントについての追加ルールは、当日のチャレンジで示します。

20点の内訳は、コードの読解と予想（5点）、修正・拡張（5点）、検証（5点）、結果と道具の使い方の説明（5点）です。
## 成績評価 / Grading
EN:

| Component | Weight | What is assessed |
| --- | ---: | --- |
| Week 01–12 assignments | **60%** | Twelve small, working, explained notebooks; each scored 0–3. |
| Week 13 final project | **20%** | Purpose, runnable result, code understanding, AI/agent judgment, verification. |
| Week 14 in-class challenge | **20%** | Individual code reading, modification, testing, and explanation. |

### Weekly 0–3 scale

| Points | Meaning |
| ---: | --- |
| **3** | Works, meets the brief, and goes beyond it with an original, well-checked choice. |
| **2** | Works, meets the brief, and explains the important choices. This is the expected standard. |
| **1** | Submitted, but key parts are incomplete, do not run, or are not explained. |
| **0** | No submission. |

For the project and the final challenge, each of four criteria is worth 5 points. The criteria are listed in their respective sections above and in the project brief. You will see the final challenge's exact prompt in class.

JP:

| 評価項目 | 配点 | 見るところ |
| --- | ---: | --- |
| Week 01〜12の課題 | **60%** | 動き、説明のある小さなNotebookを12回。各回0〜3点。 |
| Week 13の最終プロジェクト | **20%** | 目的、動く成果物、コード理解、AI／Agentの判断、検証。 |
| Week 14の授業内チャレンジ | **20%** | 個人での読解、修正、テスト、説明。 |

### 毎週の0〜3点

| 点 | 基準 |
| ---: | --- |
| **3** | 課題を満たして動き、独自の工夫があり、その工夫も確かめている。 |
| **2** | 課題を満たして動き、重要な判断を説明できる。これが標準。 |
| **1** | 提出はしたが、主要部分が未完成・動かない・説明がない。 |
| **0** | 未提出。 |

プロジェクトと最終チャレンジは、それぞれ4項目×5点で評価します。プロジェクトの詳細は要項に、最終チャレンジの具体的な問題は授業内に示します。
## 提出のしかた / Submission
EN: Submit every assignment through **UNIPA**, not by email or a link alone. Submit the completed `.ipynb` file and any data or other files it needs; add a screenshot when the prompt asks for one. Run all cells before submitting, leave the outputs in place, and write your observations in Markdown cells. A notebook that only contains code you cannot explain is not finished. Credit data, images, and outside code, and record meaningful AI or agent help. Follow the deadline displayed in UNIPA.

JP: 課題はすべて**UNIPA**から提出します。メールやリンクだけでは提出になりません。完成した`.ipynb`ファイルと、実行に必要なデータなどの関連ファイルを添えてください。スクリーンショットは課題で指定された場合に追加します。提出前にセルを最後まで実行し、出力を残し、Markdownセルに観察を書きましょう。説明できないコードを貼っただけでは完成ではありません。データ・画像・外部コードの出典、重要なAI／Agentの支援も記録してください。締切はUNIPAの表示に従います。
