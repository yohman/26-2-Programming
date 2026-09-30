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
- 1945 | Plankalkül | コンピュータが完成する前から、問題を「手順」と「値」で表そうとした最初期の高級言語。 | One of the first high-level languages: a way to express problems as steps and values before modern computers existed. | PK | https://computerhistory.org/profile/konrad-zuse/ | | R1.3 = R1.1 + R1.2 | チェスの手順、数値計算、論理問題の記述 | Chess procedures, numerical calculation, and formal logic | Konrad Zuse。実用普及よりも、言語を設計する発想を先取りした。 | Konrad Zuse; influential as a design idea rather than a widely deployed language. | 0
- 1949 | Assembly | CPUが理解する命令に、人間が読める短い名前を与えた。ハードウェアの動きがそのまま見える。 | Gave readable names to processor instructions, keeping the machine's actual behavior visible. | ASM | https://www.ibm.com/docs/en/aix/7.2.0?topic=reference-assembler-language | | MOV AX, 2⏎ADD AX, 3 | OSの核、デバイスドライバ、組み込み機器 | Operating-system kernels, device drivers, and embedded systems | CPUや機器の近くで働くシステム、組み込み、セキュリティの技術者 | Systems, embedded, and security engineers working close to hardware | 6.1
- 1957 | FORTRAN | 科学技術計算を、機械語より人間に近い数式で書けるようにした。 | Made scientific computing writable in notation much closer to mathematics than machine code. | FORTRAN | https://www.ibm.com/history/fortran | | PROGRAM HELLO⏎  PRINT *, "HELLO, WORLD!"⏎END PROGRAM HELLO | 天気予報、宇宙開発、物理シミュレーション | Weather prediction, spaceflight calculations, and scientific simulation | 科学者、技術者、スーパーコンピュータを使う研究者 | Scientists, engineers, and high-performance-computing researchers | 0
- 1958 | Lisp | コードそのものをデータとして扱い、記号や知識を操作するAI研究の道具になった。 | Treated code itself as data and became a foundational tool for symbolic computing and AI research. | LISP | https://www-formal.stanford.edu/jmc/history/lisp/lisp.html | | (format t "Hello, world!~%") | 初期AI、数式処理、Emacsの拡張 | Early AI, symbolic mathematics, and extending Emacs | AI・計算機科学の研究者、言語設計者 | AI and computer-science researchers and language designers | 0
- 1959 | COBOL | 企業や行政の大量の記録と業務を、コードで扱う基盤をつくった。 | Put large-scale business and government records into programmable systems. | COBOL | https://www.computerhistory.org/tdih/may/28/ | | IDENTIFICATION DIVISION.⏎PROGRAM-ID. HELLO.⏎PROCEDURE DIVISION.⏎  DISPLAY "HELLO, WORLD!".⏎  STOP RUN. | 銀行勘定、給与計算、行政・保険の基幹システム | Banking, payroll, insurance, and government record systems | 大企業・行政のメインフレーム技術者 | Mainframe programmers in large enterprises and government | 0
- 1964 | BASIC | 初心者がすぐに試せる対話的な言語として、学校とパーソナルコンピュータに広がった。 | Made programming immediately approachable in classrooms and on early personal computers. | BASIC | https://home.dartmouth.edu/about/dartmouth-milestones/1964-basic | | 10 PRINT "HELLO, WORLD!"⏎20 GOTO 10 | 学校教育、8-bit PCのゲームや小さな道具 | Classroom learning and games or utilities on 8-bit home computers | 学生、教師、初期PCのホビイスト | Students, teachers, and early personal-computer hobbyists | 0
- 1972 | C | 小さく速い言語でUNIXをつくり、ソフトウェアを別の機械へ移せるようにした。 | Made it practical to build Unix in a compact, portable language. | C | https://www.nokia.com/bell-labs/about/dennis-m-ritchie/chist.html | | #include <stdio.h>⏎⏎int main(void) {⏎  printf("Hello, world!\\n");⏎  return 0;⏎} | UNIX、OS、組み込み機器、言語処理系 | Unix, operating systems, embedded devices, and language runtimes | システム、組み込み、性能重視のソフトウェア技術者 | Systems, embedded, and performance-oriented engineers | 22.0
- 1972 | Smalltalk | オブジェクトと画面上の操作を結びつけ、今のGUIとアプリ設計に大きな影響を与えた。 | Joined objects with graphical interaction, shaping modern interfaces and application design. | ST | https://computerhistory.org/blog/smalltalk-at-50/ | | Transcript⏎  show: "Hello, world!";⏎  cr. | Xerox AltoのGUI、オブジェクト指向設計 | The Xerox Alto interface and object-oriented application design | GUI研究者、教育者、オブジェクト指向の設計者 | Interface researchers, educators, and object-oriented designers | 0
- 1974 | SQL | データに「どう処理するか」ではなく「何がほしいか」を問い合わせられるようにした。 | Let people ask for the data they want instead of prescribing every processing step. | SQL | https://www.ibm.com/history/relational-model-database | | SELECT "Hello, world!" AS message; | 銀行、予約、EC、分析など、ほぼすべてのデータベース | Databases behind banking, reservations, commerce, and analytics | データ分析、バックエンド、データベースの技術者 | Data analysts, back-end developers, and database engineers | 58.6
- 1985 | C++ | Cの速度と制御を保ちながら、大規模なソフトウェアを構造化する仕組みを加えた。 | Added tools for structuring large software while retaining C-like speed and control. | C++ | https://isocpp.org/about/history-of-cpp | | #include <iostream>⏎int main() {⏎  std::cout << "Hello, world!";⏎} | ゲームエンジン、ブラウザ、映像、リアルタイム処理 | Game engines, browsers, graphics, and real-time software | ゲーム、システム、高性能計算の技術者 | Game, systems, and high-performance-computing engineers | 23.5
- 1991 | Python | 読みやすさを中心に置き、学習、科学、データ、AIを同じ言語でつないだ。 | Put readability first, connecting learning, science, data, and AI in one language. | assets/timeline/python-logo.svg | https://www.python.org/about/apps/ | | name = "world"⏎print(f"Hello, {name}!") | AI、データ分析、科学計算、Web、業務自動化 | AI, data analysis, science, web services, and automation | 学習者から研究者、データ・AI・Web技術者まで | Learners, researchers, and data, AI, and web developers | 57.9
- 1995 | Java | 一度書いたプログラムを、多くの異なる環境で動かす考えを広めた。 | Popularized the idea of writing software once and running it across many environments. | JAVA | https://www.oracle.com/a/ocom/docs/dc/ww-brief-history-java-infographic.pdf | | class Hello {⏎  public static void main(String[] args) {⏎    System.out.println("Hello, world!");⏎  }⏎} | Android、企業システム、サーバー、Minecraft | Android, enterprise systems, servers, and Minecraft | 企業のバックエンド・業務システム・Android技術者 | Enterprise back-end, business-system, and Android developers | 29.4
- 1995 | JavaScript | Webページを「読むもの」から、反応し動くソフトウェアへ変えた。 | Turned the web from pages we read into software that responds and moves. | JS | https://developer.mozilla.org/en-US/docs/Glossary/JavaScript | | const name = "world";⏎console.log("Hello, " + name + "!"); | Google MapsのようなWebアプリ、Node.js、対話的なサイト | Interactive web apps such as Google Maps, Node.js, and dynamic sites | フロントエンド・フルスタック・Web技術者 | Front-end, full-stack, and web developers | 66.0
- 2007 | Scratch | ブロックを組み合わせ、子どもも物語、ゲーム、動きをコードでつくれるようにした。 | Let young creators build stories, games, and motion by snapping blocks together. | assets/timeline/scratch-logo.svg | https://news.mit.edu/2007/resnick-scratch | | when green flag clicked⏎say [Hello, world!] for (2) seconds | 物語、アニメーション、ゲーム、プログラミング教育 | Stories, animation, games, and introductory computing education | 子ども、初学者、教師、クリエイティブ・コーダー | Children, beginners, teachers, and creative coders | 0
- 2009 | Go | 大規模なネットワークサービスを、読みやすく、速く、安全に並行処理するためにつくられた。 | Was designed to make large networked systems readable, fast, and practical to build concurrently. | GO | https://go.dev/doc/faq | | package main⏎import "fmt"⏎func main() {⏎  fmt.Println("Hello, world!")⏎} | Docker、Kubernetes、クラウド基盤、ネットワークサービス | Docker, Kubernetes, cloud infrastructure, and network services | クラウド、SRE、バックエンド、基盤技術者 | Cloud, SRE, back-end, and infrastructure engineers | 16.4
- 2010 | Rust | メモリ安全性と高い性能を両立し、低レベルのバグをコンパイル時に防ぐ。 | Combines memory safety with high performance, preventing many low-level bugs before a program runs. | RUST | https://rust-lang.org/what/ | | fn main() {⏎  println!("Hello, world!");⏎} | Firefox、OS部品、組み込み、WebAssembly | Firefox, operating-system components, embedded software, and WebAssembly | システム、セキュリティ、基盤技術者 | Systems, security, and infrastructure engineers | 14.8
- 2012 | TypeScript | JavaScriptに型を加え、大きなWebアプリをチームで安全に変更しやすくした。 | Added types to JavaScript so teams could change large web applications more safely. | TS | https://www.typescriptlang.org/why-create-typescript/ | | const message: string = "Hello, world!";⏎console.log(message); | VS Code、大規模Webアプリ、Node.jsサービス | VS Code, large web applications, and Node.js services | フロントエンド、フルスタック、大規模Web開発チーム | Front-end, full-stack, and large web-development teams | 43.6
- 2014 | Swift | Apple製品向けのアプリを、安全で現代的な文法でつくるために設計された。 | Was designed as a safe, modern language for building software across Apple platforms. | SWIFT | https://www.swift.org/about/ | | let message = "Hello, world!"⏎print(message) | iPhone、iPad、Mac、Apple Watchのアプリ | Apps for iPhone, iPad, Mac, and Apple Watch | Appleプラットフォームのアプリ開発者 | Developers building apps for Apple platforms | 5.4
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
