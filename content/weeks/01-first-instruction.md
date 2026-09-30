---
week: 1
publish_at: 2026-09-29T09:00:00+09:00
preview: true
phase: WRITE
practice_mix: Human 85% · AI 10% · Agent 5%
practice_mix_ja: 人 85% · AI 10% · エージェント 5%
title: Make the computer say something.
title_ja: コンピュータに「してほしいこと」を伝える。
course_date: 2026-10-01
course_time: 13:10–14:50
overview: Build your personal Python workspace, run your first notebook, and make a small calculator that someone else can use.
overview_ja: 自分のPython作業環境をつくり、最初のノートブックを実行し、誰かが使える小さな計算機をつくる。
---
## Lecture Timelines
### journey
- 1982 | NEC PC-6001 | 私の出発点。キーボードから命令を入力すると、画面が応えることを知った。PC-6001自体の発売は1981年11月。 | My starting point: type an instruction, and the screen answers. The PC-6001 itself was released in November 1981. | assets/timeline/nec-pc-6001.jpg | https://support.nec-lavie.jp/navigate/application/history/20120828/index02.html | https://commons.wikimedia.org/wiki/File:NEC_PC-6001.jpg
- 1980s | NEC PC-8801 | 文字だけでなく、色、音、ゲームへ。コードが体験をつくれることが見えてきた。PC-8801の発売も1981年11月。 | Beyond text: color, sound, and games made it clear that code could create an experience. The PC-8801 was also released in November 1981. | assets/timeline/nec-pc-8801.jpg | https://akiba-pc.watch.impress.co.jp/docs/column/retrosoft/1052380.html | https://commons.wikimedia.org/wiki/File:NEC_PC-8801_with_keyboard.jpg
- 1993 | Macintosh Color Classic | コンピュータが「道具」であるだけでなく、触れて使いたくなるデザインにもなった。 | A computer became more than a tool: it became something designed to invite use. | assets/timeline/macintosh-color-classic.jpg | https://support.apple.com/en-us/112200 | https://commons.wikimedia.org/wiki/File:Macintosh_Colour_Classic_1994.jpg
- 2006 | MacBook Pro · Intel | PowerBookからMacBook Proへ。持ち歩けるコンピュータが、つくるための中心になった。 | From PowerBook to MacBook Pro: a portable computer became the center of making. | assets/timeline/macbook-pro-2006.jpg | https://www.apple.com/jp/newsroom/2006/01/10Apple-Introduces-MacBook-Pro/ | https://commons.wikimedia.org/wiki/File:MacBook_Pro.jpg
- 2012 | MacBook Pro · Retina | コード、文字、画像を高精細な画面で扱う。つくる場所と見る場所が一つになった。 | Code, type, and images met on a high-resolution screen—the place for making and viewing became one. | assets/timeline/macbook-pro-retina-2012.jpg | https://www.apple.com/newsroom/2012/10/23Apple-Introduces-13-inch-MacBook-Pro-with-Retina-Display/ | https://commons.wikimedia.org/wiki/File:Retina_MB_Pro.jpg
- 2021 | MacBook Pro · Apple silicon | CPUの世代が変わり、同じノート型の中でできることが大きく広がった。 | A new processor era expanded what the same notebook form could do. | assets/timeline/macbook-pro-2021.jpg | https://www.apple.com/uk/newsroom/2021/10/apple-unveils-game-changing-macbook-pro/ | https://commons.wikimedia.org/wiki/File:A_2021_14-inch_Silver_MacBook_Pro_(cropped).jpg
### languages
- 1957 | FORTRAN | 科学技術計算を、機械語より人間に近い言葉で書けるようにした。 | Made scientific computing writable in a language closer to human notation than machine code. | FORTRAN | https://www.ibm.com/history/fortran
- 1959 | COBOL | 企業や行政の大量の記録と業務を、コードで扱う基盤をつくった。 | Put large-scale business and government records into programmable systems. | COBOL | https://www.computerhistory.org/tdih/may/28/
- 1972 | C | 小さく速い言語でOSをつくり、ソフトウェアを別の機械へ移せるようにした。 | Made it practical to build an operating system in a compact, portable language. | C | https://www.nokia.com/bell-labs/about/dennis-m-ritchie/chist.html
- 1972 | Smalltalk | オブジェクトと画面上の操作を結びつけ、今のGUIとアプリ設計に大きな影響を与えた。 | Joined objects with graphical interaction, shaping modern interfaces and application design. | ST | https://computerhistory.org/blog/smalltalk-at-50/
- 1991 | Python | 読みやすさを中心に置き、学習、科学、データ、AIを同じ言語でつないだ。 | Put readability first, connecting learning, science, data, and AI in one language. | assets/timeline/python-logo.svg | https://docs.python.org/3.10/license.html
- 1995 | Java | 一度書いたプログラムを、多くの異なる環境で動かす考えを広めた。 | Popularized the idea of writing software once and running it across many environments. | JAVA | https://www.oracle.com/a/ocom/docs/dc/ww-brief-history-java-infographic.pdf
- 1995 | JavaScript | Webページを「読むもの」から、反応し動くソフトウェアへ変えた。 | Turned the web from pages we read into software that responds and moves. | JS | https://developer.mozilla.org/en-US/docs/Glossary/JavaScript
- 2007 | Scratch | ブロックを組み合わせ、子どもも物語、ゲーム、動きをコードでつくれるようにした。 | Let young creators build stories, games, and motion by snapping blocks together. | assets/timeline/scratch-logo.svg | https://news.mit.edu/2007/resnick-scratch
## Tutorials
- [Pythonをインストールする / Install Python](weeks/week-01/tutorials/01-install-python.md) {tutorial}
- [VS Codeを準備する / Set up VS Code](weeks/week-01/tutorials/02-install-vscode.md) {tutorial}
- [授業フォルダをつくる / Create the course workspace](weeks/week-01/tutorials/03-course-workspace.md) {tutorial}
- [`.venv`とKernelをつなぐ / Environment and kernel](weeks/week-01/tutorials/04-environment-and-kernel.md) {tutorial}
- [Jupyter Notebookの使い方 / Use a notebook](weeks/week-01/tutorials/05-jupyter-notebook.md) {tutorial}
- [Markdownで説明を書く / Markdown basics](weeks/week-01/tutorials/06-markdown-basics.md) {tutorial}
- [Python BasicsとローカルChallenge / Python basics](weeks/week-01/tutorials/07-python-basics-and-challenges.md) {tutorial}
## In-Class Notebook
EN: Set up your own Python notebook, then write and run your first small programs. You will work with output, values, variables, and input.
JP: 自分のPythonノートブックを準備し、最初の小さなプログラムを書いて実行する。出力、値、変数、入力を扱う。
## In-Class Challenge
EN: Make a Mini Personal Calculator: two inputs, one useful calculation, and one clear result. A partner should be able to run it.
JP: 二つの入力、一つの役に立つ計算、読みやすい結果を持つミニ生活計算機を作る。ペアが実行できる状態にする。
## Take-Home Assignment
EN: Make a first tiny tool that is *not* the class calculator: a personal card, mini story, game-start screen, plan, or other one-screen experience. It should use your own words and inputs, then create one clear output someone will want to see. Submit the notebook and one screenshot. Be ready to show it in Week 02.
JP: 授業内の計算機とは別に、はじめてのミニツールをつくる。プロフィールカード、ミニストーリー、ゲーム開始画面、予定カードなど、1画面で見せられる自分らしい作品にする。自分の言葉と入力を使い、見せたくなる一つの出力をつくろう。ノートブックとスクリーンショットを提出し、Week 02で紹介できるようにする。
## Aha!
EN:
```python
score = score + 5
```

This is not a mathematical claim. It replaces the value currently remembered under `score`.
JP:
```python
score = score + 5
```

これは数式の主張ではない。`score`という名前で今覚えている値を、新しい値に置き換える命令である。
## Takeaway
EN: A program is a sequence of small instructions whose values change in a traceable way.
JP: プログラムは、追跡できる形で値を変えていく小さな命令の連なりである。
## Resources
- [Week 01 In-Class — First Python](weeks/week-01/week-01-in-class-first-python.ipynb) {notebook}
- [Week 01 Challenge — Mini Personal Calculator](weeks/week-01/week-01-challenge-mini-personal-calculator.ipynb) {challenge}
- [Week 01 Take-Home — My First Tiny Tool](weeks/week-01/week-01-take-home-my-first-tiny-tool.ipynb) {homework}
- [Week 01 Setup — Python, VS Code, and Jupyter](weeks/week-01/week-01-setup-python-vscode-jupyter.md) {support}
